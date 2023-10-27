import asyncio
import re
import sys
import time
from datetime import datetime
from itertools import groupby

from a_songbo.vn.books.variety_book import VarietyBook
from a_songbo.vn.configs.vn_config import grid_trade_futures
from a_songbo.vn.ss.ss_grpc.ss_grpc_server import StrategyGrpcServer
from a_songbo.vn.ss.portfilio_process import PortfilioProcess
from a_songbo.vn.ss.strategy_gateway import StrategyGateway
from a_songbo.vn.util import thread
from a_songbo.vn.util.sys_exception import common_exception


class GridTrade:
    def __init__(self):
        self.grid_trade_futures = grid_trade_futures
        self.ss_gateway = StrategyGateway()

    def start(self):
        # 订阅行情
        self.ss_gateway.ms_stub.subscribe_stream_in_new_thread(instruments=self.grid_trade_futures,
                                                               on_quote=self.on_quote)
        self.ss_gateway.sub_instrument.update(set(self.grid_trade_futures))

        while 1:
            pass

    def on_quote(self, quote):
        quote = {k: v for k, v in quote.items()}

        timestamp_diff = float(time.time()) - float(quote['timestamp'])
        print('---', quote['InstrumentID'], timestamp_diff*1000, quote)
        return


if __name__ == '__main__':
    GridTrade().start()
