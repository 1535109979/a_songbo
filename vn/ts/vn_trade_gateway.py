import logging
import os
import time
from typing import Optional, Callable, Iterable, List, Tuple

from google.protobuf import timestamp_pb2

from a_songbo.vn.configs.vn_config import ctp_setting
from a_songbo.vn.enums.exchange_enum import *
from a_songbo.vn.proto import account_position_pb2, strategy_server_pb2_grpc, strategy_server_pb2
from a_songbo.vn.ss.ss_grpc.ss_grpc_stub import StrategyGrpcStub
from a_songbo.vn.ts.api.vn_td_api import VnCtpTdApi
from a_songbo.vn.util.dingding import Dingding
from a_songbo.vn.util.sys_exception import common_exception


class VnTdGateway():
    def __init__(self):
        self.logger = None
        self.create_logger()

        self.directions: Tuple[Direction, Direction] = (Direction.LONG, Direction.SHORT)

        # 登录成功回调函数
        self.on_login: Optional[Callable] = None

        self.ss_stub = StrategyGrpcStub()

        self.client = VnCtpTdApi(self)

        self.account_book = self.client.account_book

        # 设置交易账户信息对象
        # uai_do.account_book = self.client.account_book

    def create_logger(self):
        self.logger = logging.getLogger('td_gateway_log')
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('/Users/edy/byt_pub/a_songbo/vn/vn_logs/td_gateway.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    @property
    def get_configs(self):

        return ctp_setting

    def send_msg(self, text: str, isatall=False):
        Dingding.send_msg(text, isatall=isatall)

    @common_exception(log_flag=True)
    def insert_order(self, instrument: str, exchange_type: str,
                       volume: int, price: float,
                      order_price_type: OrderPriceType,
                      offset_flag: OffsetFlag, direction: Direction) -> str:
        try:
            """ 向交易所报单 """
            min_volume_step = self.client.account_book.get_instrument_book\
                                                    (instrument + '.' + exchange_type).min_volume_value
            if not volume % min_volume_step == 0:
                self.logger.error(f'<_insert_order> volume divisibe error volume={volume} '
                                  f'min_volume_step={min_volume_step}')
                return '0'

            return self.client.insert_order(
                instrument=instrument, exchange_type=ExchangeType.get_by_value(exchange_type),
                offset_flag=OffsetFlag.get_by_value(offset_flag), direction=direction,
                order_price_type=OrderPriceType.get_by_value(order_price_type),
                volume=volume, price=price)
        except:
            self.send_msg(f'下单错误  \ninstrument={instrument}  \nexchange_type={exchange_type}  \n'
                          f'volume={volume}  \nprice={price}  \norder_price_type={order_price_type}  \n'
                          f'offset_flag={offset_flag}  \ndirection={direction}')

    def stop(self):
        """ 退出交易柜台 """
        try:
            self.client.close()
            self.logger.info('td api stop')
        except Exception as e:
            self.logger.exception("!!! %s !!!", e)

    def on_error(self, msg):
        print(msg)

    @common_exception(log_flag=True)
    def on_account_update(self, instruments=None, need_instrument_books: bool = False):
        """ 账户信息变动 """

        mo: account_position_pb2.AccountBook = self.create_account_book_mo(
            instruments=instruments, need_instrument_books=need_instrument_books)
        # for position_mo in mo.positions:
        #     self.uai_do.upsert_by_position_mo(position_mo=position_mo)

        stub: strategy_server_pb2_grpc.StrategyStub = self.ss_stub.get_stub()
        if stub:
            stub.on_account_update(mo)

    @common_exception(log_flag=True)
    def on_trade(self, data: dict):
        data = {k: str(v) for k, v in data.items() if v is not None}
        mo: account_position_pb2.AccountBook = self.create_account_book_mo()
        rtn_mo = strategy_server_pb2.RtnRecord(
            rtn=data, account_book=mo)

        stub: strategy_server_pb2_grpc.StrategyStub = self.ss_stub.get_stub()
        if stub:
            stub.on_trade_rtn(rtn_mo)

    def create_account_book_mo(self, instruments=None, need_instrument_books=False) \
            -> account_position_pb2.AccountBook:
        """
        创建 account_position_pb2.AccountBook 实例
        @param instruments: =None时表示返回所有持仓信息，=[]时表示不返回持仓信息
        @param need_instrument_books: 是否返回合约属性字典
        """
        if instruments is not None:
            if isinstance(instruments, str):
                instruments: set = {instruments}
            elif isinstance(instruments, Iterable):
                instruments = set(instruments)

        need_get_book_instruments: set = instruments
        if need_instrument_books and not need_get_book_instruments:
            need_get_book_instruments = set()

        create_ts = timestamp_pb2.Timestamp()
        create_ts.GetCurrentTime()

        # positions (instruments=[]时不返回持仓信息)
        if instruments is not None and len(instruments) == 0:
            position_mos: Optional[list] = None
        else:
            position_mos: List[account_position_pb2.Position] = \
                self.get_instrument_position_mos(instruments=instruments)

        # instrument_books
        instrument_book_mos: Optional[list] = None
        if need_instrument_books:
            if position_mos:
                need_get_book_instruments.update({o.instrument for o in position_mos})
            if need_get_book_instruments:
                instrument_book_mos: List[account_position_pb2.InstrumentBook] = \
                    self.get_instrument_book_mos(instruments=need_get_book_instruments)

        mo = account_position_pb2.AccountBook(
            create_ts=create_ts, avail=self.account_book.avail,
            positions=position_mos or None, instrument_books=instrument_book_mos or None)

        if position_mos and len(position_mos) == 1:
            self.logger.info(
                "<position> %s %s avail=%s cts=%s", mo.account_id, position_mos[0],
                mo.avail, mo.create_ts.ToMicroseconds())
        return mo

    def get_instrument_book_mos(self, instruments=None) \
            -> List[account_position_pb2.InstrumentBook]:
        if self.account_book:
            return [
                account_position_pb2.InstrumentBook(
                    instrument=v.instrument, product_class=str(v.product_class),
                    price_tick=v.min_price_step, contract_multiplier=v.contract_multiplier,
                    long_margin_ratio=v.long_margin_ratio, short_margin_ratio=v.short_margin_ratio)
                for v in self.account_book.instrument_books.values()
                if not instruments or v.instrument in instruments]

    def get_positions(self, instruments=None, direction: Direction = None, mfn: Callable = None) \
            -> list:
        position_list = list()
        if self.account_book:
            direction: Direction = Direction.get_by_value(direction)
            directions: tuple = self.directions \
                if not direction or direction.is_bi_or_net() else (direction,)

            for book in self.account_book.position_books.values():
                if instruments and book.instrument not in instruments:
                    continue

                for direction in directions:
                    position = book.get_by_direction(direction=direction)
                    if not position.default:  # 过滤掉没有持仓数据的对象, 减少传输数据量
                        position_list.append(mfn(position, direction) if mfn else position)

        return position_list

    def get_instrument_position_mos(self, instruments=None, direction: Direction = None) \
            -> List[account_position_pb2.Position]:
        if self.account_book:
            return self.get_positions(
                instruments=instruments, direction=direction,
                mfn=lambda p, d: self.create_position_mo(
                    direction=d, instrument=p.instrument, exchange=p.exchange_type,
                    volume=p.volume, yd=p.yd, sellable=p.sellable, locked=p.locked,
                    open_avg=p.open_avg, avg=p.avg, cost=p.cost, margin=p.margin))

    def create_position_mo(self, instrument, direction, exchange, margin=0,
                           volume=0, yd=0, sellable=None, locked=0,
                           open_avg=0, avg=0, cost=0, default=False) -> account_position_pb2.Position:
        """
        创建持仓信息对象
        @param instrument: 标的
        @param direction: 多空方向
        @param exchange: 所在交易所
        @param volume: 持仓数量
        @param yd: 持昨仓数量
        @param sellable: 可平仓的数量
        @param locked: 冻结数量
        @param margin: 占用的保证金额
        @param default: 等于True时表示时从交易所获取的, 否则表示自定义的
        @param cost: 持仓成本价, 从建仓开始计算, 开平仓对成本价都有影响
        @param avg: 开仓均价, 计算从建仓开始的开仓均价, 不受部分平仓的影响
        @param open_avg: 当前持仓的开仓均价, 交易所的开仓均价
        """
        if sellable is None:
            sellable = volume

        return account_position_pb2.Position(
            instrument=instrument, direction=str(direction), exchange=str(exchange), default=default,
            margin=margin, volume=volume, yd=yd, sellable=sellable, locked=locked,
            avg=avg, cost=cost, open_avg=open_avg)


if __name__ == '__main__':
    gateway = VnTdGateway()
    gateway.client.connect()
    # time.sleep(180)

    gateway.insert_order(instrument='rb2410',exchange_type=ExchangeType.SHFE,volume=1,price=3668,
                          order_price_type=OrderPriceType.LIMIT,offset_flag=OffsetFlag.OPEN,direction=Direction.LONG)
    # gateway.query_account()
    # gateway.cancel_order()

    while 1:
        time.sleep(30)


