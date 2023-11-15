import logging
import threading
from collections import defaultdict
from typing import Dict

import numpy as np
import pandas as pd
from scipy import optimize
from scipy.stats import norm

from a_songbo.vn.data.process_sqlite import Options, Minprice, HistoryPrice
from a_songbo.vn.ms.ms_grpc.market_grpc_stub import VnMarketStub
from a_songbo.vn.proto import account_position_pb2
from a_songbo.vn.ss.ss_schelar import SsSchelar
from a_songbo.vn.ss.trade_process import TradeProcess
from a_songbo.vn.util.dingding import Dingding
from a_songbo.vn.util.sys_exception import common_exception
from a_songbo.vn.configs.vn_config import strategy_config


class StrategyGateway:

    def __init__(self):
        self.logger = None
        self.create_logger()

        # {instrument: quote}
        self.last_price = defaultdict(dict)
        self.saved_price = defaultdict(dict)
        # 记录开仓后的最低价格
        # {instrument: {'price': price, 'timestamp': time.time()}}
        self.min_price = defaultdict(dict)
        # {instrument: {'imp': imp, 'timestamp': time.time()}}
        self.last_imp = defaultdict(dict)
        self.saved_imp = defaultdict(dict)

        self.load_last_saved_imp_and_min_price()

        self.strategy_config = strategy_config

        self.left_day_map = {}

        self.expire_options = pd.read_csv('../data/expire_options.csv')
        self.expire_options.columns = ['idex', 'code', 'expire_day', 'exchange', 'left_day', 'datetime']
        self.set_left_day_map()

        self.sub_instrument = set()
        self.in_tradinng_time = True

        self._account_book: account_position_pb2.AccountBook = None
        self._last_create_ts = None
        self.avail = None

        # 合约属性字典 { instrument: account_position_pb2.InstrumentBook }
        self._instrument_books: Dict[str, account_position_pb2.InstrumentBook] = dict()

        # 合约持仓信息字典 { instrument: { direction: account_position_pb2.Position } }
        self._instrument_positions: defaultdict = defaultdict(dict)

        self.ms_stub = VnMarketStub()
        # self.td_stub = TradeGrpcStub(self)
        self.td_process = TradeProcess(self)

        self.schedular = SsSchelar(self)
        threading.Thread(target=self.schedular.run).start()

    def load_last_saved_imp_and_min_price(self):
        from peewee import fn

        query = Minprice.select(Minprice.instrument, Minprice.price,
                                fn.MAX(Minprice.timestamp).alias('max_timestamp')).group_by(
            Minprice.instrument)
        self.min_price = {row.instrument: {'price': row.price, 'timestamp': row.max_timestamp} for row in query}
        self.logger.info(f'load min_price:{self.min_price}')

        query = HistoryPrice.select(HistoryPrice.instrument, HistoryPrice.price,
                                fn.MAX(HistoryPrice.timestamp).alias('max_timestamp')).group_by(
            HistoryPrice.instrument)
        self.saved_price = {row.instrument: {'price': row.price, 'timestamp': row.max_timestamp} for row in query}
        self.logger.info(f'load saved_price:{self.saved_price}')

    def set_left_day_map(self):
        for i in range(len(self.expire_options)):
            self.left_day_map[self.expire_options.loc[i]['code']] = {'left_day': self.expire_options.loc[i]['left_day'],
                                                                     'exchange': self.expire_options.loc[i]['exchange']}

    def add_sub(self, instruments):
        self.ms_stub.add_subscribe(instruments=instruments)
        self.sub_instrument.update(set(instruments))

    @property
    def account_book(self) -> account_position_pb2.AccountBook:
        return self._account_book

    @account_book.setter
    def account_book(self, account_book: account_position_pb2.AccountBook):
        if self._account_book:
            old_create_ts = self._account_book.create_ts.ToMicroseconds()
            new_create_ts = account_book.create_ts.ToMicroseconds()
            if old_create_ts > new_create_ts:
                self.logger.error(f"!! create_ts: old({old_create_ts}) > new({new_create_ts}) !!")
                return
        self._account_book = account_book
        self.set_by_account_book(account_book=account_book)

    @common_exception(log_flag=True)
    def set_by_account_book(self, account_book: account_position_pb2.AccountBook):
        self._last_create_ts = account_book.create_ts

        # avail
        self.set_avail(avail=account_book.avail)

        # instrument_book
        if account_book.instrument_books:
            for instrument_book in account_book.instrument_books:
                self.set_instrument_book(instrument_book=instrument_book)

        # position
        if account_book.positions:
            self._instrument_positions.clear()
            for position in account_book.positions:
                self.set_instrument_position(position=position)

    def set_avail(self, avail):
        if avail is not None:
            self.avail = avail

    def set_instrument_book(self, instrument_book: account_position_pb2.InstrumentBook):
        if not instrument_book:
            return
        self._instrument_books[instrument_book.instrument] = instrument_book
        self.logger.info("<set_instrument_book> %s", instrument_book)

    def set_instrument_position(self, position: account_position_pb2.Position):
        if not position or not position.volume:
            return

        if position.instrument not in self.sub_instrument:
            self.add_sub([position.instrument])
        self._instrument_positions[position.instrument][position.direction] = position
        self.logger.info("<set_instrument_position> %s %s %s",
                         position.instrument, position.direction,
                         str(position).replace('\"', "").replace('\n', ", "))

    def on_trade_rtn(self, data: dict):
        self.td_process.updata_by_trade_rtn(data)

    @common_exception()
    def implied_volatility(self, target_value, S, K, T, call_or_put, r=3.3 / 100):
        # 定义计算误差函数
        def error_function(sigma):
            d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)

            if call_or_put == 'C':
                call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
                return call_price - target_value
            if call_or_put == 'P':
                put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
                return put_price - target_value

        # 使用SciPy的优化函数寻找隐含波动率
        implied_volatility, = optimize.root(error_function, x0=0.5).x
        return round(implied_volatility,6)

    def send_msg(self, text: str, isatall=False):
        Dingding.send_msg(text, isatall=isatall)

    def create_logger(self):
        self.logger = logging.getLogger('ss_gateway_log')
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('/Users/edy/byt_pub/a_songbo/vn/vn_logs/ss_gateway.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def create_position_msg(self):
        # print(self._instrument_positions)
        if len(self._instrument_positions):
            msg_instrument = ''
            for instrument, value in self._instrument_positions.items():
                for direc in ['LONG', 'SHORT']:
                    if value.get(direc):
                        data = value[direc]
                        msg_instrument += (instrument + ' ' + data.direction + ' cost=' + str(data.cost) +
                                           ' volume=' + str(data.volume))

                        msg_instrument += '  \n'
            return msg_instrument
        else:
            return ''


if __name__ == '__main__':
    g = StrategyGateway()
