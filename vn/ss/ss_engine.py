import asyncio
import re
import sys
from datetime import datetime
from itertools import groupby

from a_songbo.vn.books.variety_book import VarietyBook
from a_songbo.vn.ss.ss_grpc.ss_grpc_server import StrategyGrpcServer
from a_songbo.vn.ss.portfilio_process import PortfilioProcess
from a_songbo.vn.ss.strategy_gateway import StrategyGateway
from a_songbo.vn.util import thread
from a_songbo.vn.util.sys_exception import common_exception


class StrategyEngine:
    def __init__(self):
        self.ss_gateway = StrategyGateway()

        # 期货合约衍生品映射 { future instrument : expire_options }
        self.variety_map = {}

        # 策略组合处理器 { future instrument : PortfilioProcess }
        self.portfilio_processor_map = dict()

        self.expire_options = self.ss_gateway.expire_options

        self.set_portfolios()

    def set_portfolios(self):
        options = self.expire_options['code'].tolist()

        def get_prefix(option):
            return re.match(r'([a-z]+\d+)', option).group()

        sorted_options = sorted(options)
        for key, group in groupby(sorted_options, key=get_prefix):
            self.variety_map[key] = list(group)

        for k, v in self.variety_map.items():
            variety_book = VarietyBook.create_by_data(k, v)

            p = PortfilioProcess(self.ss_gateway, variety_book)
            self.portfilio_processor_map[k] = p

    @common_exception(log_flag=True)
    def start(self):

        # 订阅行情
        self.ss_gateway.ms_stub.subscribe_stream_in_new_thread(instruments=self.variety_map.keys(),
                                                               on_quote=self.on_quote)
        self.ss_gateway.sub_instrument.update(set(self.variety_map.keys()))

        # 订阅交易服务
        res = self.ss_gateway.td_process.td_stub.sub_account()

        if res:
            position_msg = self.ss_gateway.create_position_msg()

            self.ss_gateway.send_msg(f'策略服务启动成功  \n'
                                     f'加载策略数量{len(self.ss_gateway.strategy_config["load_strategy_list"])}'
                                     f':{self.ss_gateway.strategy_config["load_strategy_list"]}  \n'
                                     f'当前持仓数量:{len(self.ss_gateway._instrument_positions)}  \n'
                                     f'{position_msg}')


        # self.ss_gateway.ms_stub.subscribe_stream_in_new_thread(instruments=['rb2311C4000', 'rb2311'],
        #                                                        on_quote=self.on_quote)
        # time.sleep(3)
        # self.ss_gateway.ms_stub.add_subscribe(instruments=['sc2311C670'])

        asyncio.run(StrategyGrpcServer(self.ss_gateway).run())

        # while 1:
        #     pass

    def on_quote(self, quote):
        quote = {k: v for k, v in quote.items()}
        for k, v in quote.items():
            if v == sys.float_info.max:
                quote[k] = 0

        # timestamp_diff = float(time.time()) - float(quote['timestamp'])
        # print('---', quote['InstrumentID'], timestamp_diff*1000, quote)
        # return
        # print(self.ss_gateway.last_price.keys())

        instrument = quote['InstrumentID']
        quote_time = datetime.strptime(quote['TradingDay'] + ' ' + quote['UpdateTime'] + ' ' + quote['UpdateMillisec'],
                                       '%Y%m%d %H:%M:%S %f').timestamp()
        quote['quote_time'] = quote_time

        self.ss_gateway.last_price[instrument] = quote

        future_instrument = re.match(r'[a-z]+\d+', instrument).group()
        p: PortfilioProcess = self.portfilio_processor_map.get(future_instrument, 0)
        if p:
            thread.submit(_executor=p.thread_pool, _fn=p.process_quote,
                          _kwargs=dict(quote=quote))


if __name__ == '__main__':
    StrategyEngine().start()
