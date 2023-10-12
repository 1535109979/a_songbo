from dataclasses import field, dataclass
from datetime import datetime

from a_songbo.vn.books.rtn_order import RtnOrder
from a_songbo.vn.enums.exchange_enum import *
from a_songbo.vn.ts.api.constant import *
from a_songbo.vn.util import type_util


@dataclass
class RtnTrade:
    """
    成交回报数据
    """

    data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.account_id = self.data["account_id"]
        self.instrument = self.data["instrument"]
        self.exchange_type = ExchangeType.get_by_value(self.data["exchange_type"])
        self.instrument_category = self.data["instrument_category"]
        self.offset_flag = self.data["offset"]
        self.direction = self.data["side"]
        self.volume = self.data["volume"]
        self.price = self.data["price"]
        self.order_id = self.data["order_id"]
        self.order_ref_id = self.data["order_ref_id"]
        self.parent_order_id = self.data["parent_order_id"]
        self.trade_id = self.data["trade_id"]
        self.trade_time = self.data["trade_time"]
        self.trading_day = self.data["trading_day"]

        self.turnover = type_util.get_precision_number(
            number=self.volume * self.price, precision=2)

        # 受影响的持仓多空方向
        self.position_direction: Direction = Direction.get_position_direction(
            direction=self.direction, offset_flag=self.offset_flag)

    @classmethod
    def create_by_rtn_data(cls, data: dict, rtn_order: RtnOrder, timezone):
        offset_flag: OffsetFlag = OFFSET_FLAG_CTP2VT[data["OffsetFlag"]]
        direction: Direction = DIRECTION_CTP2VT[data["Direction"]]

        data_datetime: datetime = datetime.strptime(
            f"{data['TradeDate']} {data['TradeTime']}", "%Y%m%d %H:%M:%S")
        data_datetime.replace(tzinfo=timezone)
        trade_time: int = int(data_datetime.timestamp() * 1000000000)

        return cls(data=dict(
            instrument_category=rtn_order.instrument_category, account_id=rtn_order.account_id,
            instrument_type=rtn_order.instrument_type, instrument=data["InstrumentID"],
            exchange_type=data["ExchangeID"], offset=offset_flag, side=direction,
            price=data["Price"], volume=data["Volume"],
            margin=data.get("margin"), profit=data.get("profit"),
            trade_time=trade_time, trading_day=data["TradingDay"],
            order_id=rtn_order.order_id, trade_id=data["TradeID"].strip(),
            parent_order_id=data["OrderSysID"].strip(), order_ref_id=data["OrderRef"].strip(),
            hedge_flag=data["HedgeFlag"], client_id=rtn_order.client_id))

    @property
    def margin(self):
        return self.data.get("margin")

    @margin.setter
    def margin(self, margin):
        self.data["margin"] = type_util.get_precision_number(
            number=margin, precision=2)

    @property
    def profit(self):
        return self.data.get("profit") or 0

    @profit.setter
    def profit(self, profit: float):
        self.data["profit"] = profit or 0

    @property
    def instrument_type(self) -> str:
        return self.data["instrument_type"]

    @property
    def id(self):
        return self.data["id"]

