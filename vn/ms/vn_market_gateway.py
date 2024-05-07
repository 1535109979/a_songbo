import asyncio
import logging
import os
import sys
import time
import traceback
from asyncio import events

from a_songbo.vn.books.quote_writer import QuoteWriter
from a_songbo.vn.configs.vn_config import ctp_setting
from a_songbo.vn.ms.vn_md_api import VnMdApi
from a_songbo.vn.proto import market_server_pb2
from a_songbo.vn.util.dingding import Dingding
from a_songbo.vn.util.sys_exception import common_exception


class VnMarketGateway():
    def __init__(self):
        self.logger = None
        self.create_logger()

        self.vn_md_api = VnMdApi(self)
        self.sub_instruments = set()
        self.quote_subscriber = dict()

        self.loop = events.new_event_loop()

    @property
    def get_configs(self):
        return ctp_setting

    def on_quote(self, quote):
        for k, v in quote.items():
            if v == sys.float_info.max:
                quote[k] = 0
        symbol = quote["InstrumentID"]
        quote = {k: str(v) for k, v in quote.items() if v is not None}
        quote['timestamp'] = str(time.time())

        if self.quote_subscriber:
            for p, q in self.quote_subscriber.items():
                if symbol in q.subscribe_symbol:
                    self.send_quote(q, quote)

    def send_msg(self, text: str, isatall=False):
        Dingding.send_msg(text, isatall=isatall)

    def send_quote(self, q, quote):
        try:
            asyncio.run_coroutine_threadsafe(q.writer.write(self.create_grpc_reply(quote=quote)), self.loop)
        except:
            traceback.print_exc()

    def on_login_success(self):
        self.send_msg('行情服务连接成功')
        for symbol in self.sub_instruments:
            self.vn_md_api.subscribe(symbol=symbol)

    def add_subscribe(self, need_sub, quote_writer:QuoteWriter):
        for symbol in need_sub:
            self.vn_md_api.subscribe(symbol=symbol)
            self.sub_instruments.update([symbol])

            if symbol not in quote_writer.subscribe_symbol:
                quote_writer.add_symbol([symbol])

    def add_subscriber(self,peer,context):
        quote_writer = QuoteWriter(context)
        self.quote_subscriber[peer] = quote_writer
        return quote_writer

    def create_grpc_reply(self,quote):
        return market_server_pb2.Quote(quote=quote)

    def get_or_create_subscriber(self,peer,context):
        quote_writer = self.quote_subscriber.get(peer)
        if not quote_writer:
            quote_writer = self.add_subscriber(peer,context)
        return quote_writer

    def write_log(self,message):
        print('write_log:',message)

    def create_logger(self):
        self.logger = logging.getLogger('ms_gateway_log')
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('/Users/edy/byt_pub/a_songbo/vn/vn_logs/ms_gateway.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

