from dataclasses import dataclass, field
from typing import Dict

from a_songbo.vn.books.instrument_book import InstrumentBook
from a_songbo.vn.books.position_book import InstrumentPositionBook, InstrumentPosition
from a_songbo.vn.books.rtn_trade import RtnTrade
from a_songbo.vn.enums.exchange_enum import Direction
from a_songbo.vn.util import type_util
from a_songbo.vn.util.lock import instance_synchronized


@dataclass
class AccountBook:
    # 账号id
    account_id: str
    # 账户资金 查询回报
    data: dict = field(default_factory=dict)

    # 持仓数据字典 { vt_symbol : InstrumentPositionBook }
    position_books: Dict[str, InstrumentPositionBook] = field(default_factory=dict)

    # 合约属性字典 { vt_symbol: InstrumentBook }
    instrument_books: Dict[str, InstrumentBook] = field(default_factory=dict)

    def update_data(self, data: dict):
        for key in ('Available', 'CurrMargin', 'Balance'):
            data[key] = type_util.get_precision_number(
                number=data.get(key), precision=2, default=0)

        self.data.update(data)

    @property
    def avail(self) -> float:
        """ 可用资金 """
        return self.data.get("Available", 0)

    @avail.setter
    def avail(self, avail: float):
        self.data["Available"] = type_util.get_precision_number(
            number=avail, precision=2, default=0)

    @property
    def margin(self) -> float:
        """ 占用保证金 """
        return self.data.get("CurrMargin", 0)

    @margin.setter
    def margin(self, margin: float):
        self.data["CurrMargin"] = type_util.get_precision_number(
            number=margin, precision=2, default=0)

    @property
    def frozen(self) -> float:
        """ 冻结资金 """
        return self.data["FrozenMargin"] + self.data["FrozenCash"] + self.data["FrozenCommission"]

    @property
    def balance(self) -> float:
        """ 当前权益 """
        return self.data.get("Balance", 0)

    def get_instrument_book(self, vt_symbol: str) -> InstrumentBook:
        """ 获取合约属性 """
        instrument_book: InstrumentBook = self.instrument_books.get(vt_symbol)
        if not instrument_book:
            instrument_book = InstrumentBook(vt_symbol=vt_symbol)
            self.instrument_books.setdefault(vt_symbol, instrument_book)
        return instrument_book

    def get_instrument_position(self, vt_symbol: str, direction: Direction) -> InstrumentPosition:
        """ 查询合约指定多空方向的持仓数量 """
        return self.get_instrument_position_book(vt_symbol).get_by_direction(direction=direction)

    def get_instrument_position_book(self, vt_symbol: str) -> InstrumentPositionBook:
        """ 查询合约持仓信息 """
        book: InstrumentPositionBook = self.position_books.get(vt_symbol)
        if not book:
            book = InstrumentPositionBook(vt_symbol=vt_symbol)
            self.position_books.setdefault(vt_symbol, book)
        return book

    @instance_synchronized
    def update_by_trade_rtn(self, rtn: RtnTrade) -> InstrumentPosition:
        """ 根据成交回报信息更新账户和持仓信息 """
        vt_symbol = f'{rtn.instrument}.{rtn.exchange_type}'
        instrument_book: InstrumentBook = self.get_instrument_book(vt_symbol=vt_symbol)
        position: InstrumentPosition = self.get_instrument_position(
            vt_symbol=vt_symbol, direction=rtn.position_direction)
        position.update_by_trade_rtn(rtn=rtn, instrument_book=instrument_book)

        # 更新账户可用资金和保证金
        self.avail -= rtn.margin
        self.margin += rtn.margin
        return position
