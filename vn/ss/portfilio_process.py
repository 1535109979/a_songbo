import importlib
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from a_songbo.vn.books.variety_book import VarietyBook
from a_songbo.vn.ss.strategy_gateway import StrategyGateway
from a_songbo.vn.ss.strategys import SellStrategy
from a_songbo.vn.util.lock import instance_synchronized
from a_songbo.vn.util.sys_exception import common_exception


class_name = "SellStrategy"
module_name = "a_songbo.vn.ss.strategys"  # 替换为实际的模块名称


class PortfilioProcess:
    def __init__(self, gateway: StrategyGateway, variety_book):
        self.long_trading: bool = False
        self.short_trading: bool = False

        self.gateway = gateway
        self.variety_book: VarietyBook = variety_book

        self.strategys_list = []
        self.load_strategy()

        self.thread_pool = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="ss-{}".format(self.variety_book.future))

    def load_strategy(self):
        module = importlib.import_module(self.gateway.strategy_config['module_name'])
        for class_name in self.gateway.strategy_config['load_strategy_list']:
            class_ = getattr(module, class_name)
            cl = class_(self.gateway, self)
            self.strategys_list.append(cl)

    @common_exception(log_flag=True)
    def process_quote(self, quote):

        instrument = quote['InstrumentID']

        # 更新期货合约价格，更新期权合约档位
        if instrument == self.variety_book.future:
            self.update_variety_book(quote=quote)
            return
        else:
            # 计算期权隐含波动率
            self.cal_imp(quote)

        if not self.check_quote_time_diff(quote):
            return

        # 是否在交易时间
        if not self.gateway.in_tradinng_time:
            return

        # 检查可用资金
        if not self.gateway.avail or self.gateway.avail < self.gateway.strategy_config['avail_down']:
            return

        for cl in self.strategys_list:
            cl.cal_signal(quote)
        # print()

    def check_quote_time_diff(self, quote):
        # 检查行情时间是否超时
        now_time = time.time()
        quote_time_diff = round(float(now_time) - float(quote['quote_time']), 6)
        process_time_diff = round(float(now_time) - float(quote['timestamp']), 6)

        if process_time_diff > 3:
            self.gateway.logger.info(f'收到{quote["InstrumentID"]} 行情超时,'
                                  f'quote_time_diff={quote_time_diff}，process_time_diff={process_time_diff}')
            self.gateway.send_msg(f'收到{quote["InstrumentID"]} 行情超时  \n'
                                  f'quote_time_diff={quote_time_diff}，process_time_diff={process_time_diff}')
            return False

        return True

    def update_variety_book(self, quote):
        self.variety_book.update_by_future_price(float(quote['LastPrice']))

        if self.variety_book.long_virtual_2.option and self.variety_book.long_virtual_2.option not in self.gateway.sub_instrument:
            self.gateway.add_sub([self.variety_book.long_virtual_2.option])
        if self.variety_book.short_virtual_2.option and self.variety_book.short_virtual_2.option not in self.gateway.sub_instrument:
            self.gateway.add_sub([self.variety_book.short_virtual_2.option])

    @common_exception(log_flag=True)
    def cal_imp(self, quote):
        option_price = round(float(quote['LastPrice']), 2)
        future_last_data = self.gateway.last_price.get(self.variety_book.future, 0)
        if not future_last_data:
            return
        future_price = round(float(future_last_data['LastPrice']), 2)

        strike_price = None
        call_or_put = None
        t = None

        if quote['InstrumentID'] == self.variety_book.long_virtual_2.option:
            strike_price = self.variety_book.long_virtual_2.strike_price
            call_or_put = 'C'
            t = self.gateway.left_day_map.get(self.variety_book.long_virtual_2.option)['left_day'] / 365
        if quote['InstrumentID'] == self.variety_book.short_virtual_2.option:
            strike_price = self.variety_book.short_virtual_2.strike_price
            call_or_put = 'P'
            t = self.gateway.left_day_map.get(self.variety_book.short_virtual_2.option)['left_day'] / 365

        if option_price and future_price and strike_price and call_or_put and t:
            imp = self.gateway.implied_volatility(target_value=option_price, S=future_price, K=strike_price,
                                       call_or_put=call_or_put, T=t)
            # print(instrument, imp, float(time.time()) - float(quote['timestamp']))
            self.gateway.last_imp[quote['InstrumentID']] = {'imp': imp, 'timestamp': quote['quote_time']}
            # print(len(self.gateway.last_imp))
