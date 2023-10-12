import time
from dataclasses import field, dataclass
from datetime import datetime

from a_songbo.vn.enums.exchange_enum import ExchangeType, InstrumentCategory
from a_songbo.vn.ts.api.constant import *
from a_songbo.vn.util import type_util
from a_songbo.vn.util.lock import instance_synchronized


@dataclass
class RtnOrder:
    """
    下单回报数据
    """
    data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.account_id = self.data["account_id"]
        self.instrument = self.data["instrument"]
        self.exchange_type = ExchangeType.get_by_value(self.data["exchange_type"])
        self.instrument_category = self.data["instrument_category"]
        self.offset_flag = self.data["offset"]
        self.direction = self.data["side"]
        self.insert_time = self.data["insert_time"]
        self.trading_day = self.data["trading_day"]
        self.order_id = self.data["order_id"]
        self.order_ref_id = self.data["order_ref_id"]

        # 受影响的持仓多空方向
        self.position_direction: Direction = Direction.get_position_direction(
            direction=self.direction, offset_flag=self.offset_flag)

        # 设置默认值使属性统一
        self.data.setdefault("parent_order_id", "")
        self.data.setdefault("client_id", 0)
        self.data.setdefault("is_swap", 0)
        self.data.setdefault("turnover", 0)
        self.data.setdefault("volume_traded", 0)
        self.data.setdefault("error_id", 0)
        self.data.setdefault("error_msg", "")
        self.data.setdefault("update_time", self.insert_time)
        self.data.setdefault("instrument_type", 'future')

    def update_data(self, data: dict):
        self.data.update(data)
        self.__post_init__()

    @instance_synchronized
    def update_by_rtn_data(self, data: dict, timezone):
        order_sys_id: str = data["OrderSysID"].strip()

        data_datetime: datetime = datetime.strptime(
            f"{data['InsertDate']} {data['InsertTime']}", "%Y%m%d %H:%M:%S")
        data_datetime.replace(tzinfo=timezone)
        update_time = data_datetime.timestamp() * 1000000000

        limit_price: float = data.get("LimitPrice", 0)
        volume_traded: float = data.get("VolumeTraded", 0)
        turnover: float = type_util.get_precision_number(
            number=volume_traded * limit_price, precision=2)

        order_status: str = data.get("OrderStatus", THOST_FTDC_OST_Unknown)
        status: OrderStatus = STATUS_CTP2VT.get(order_status, OrderStatus.UNKNOWN)

        error_id = data.get("ErrorID", self.error_id)
        error_msg = data.get("ErrorMsg", self.error_msg)

        self.update_data(data=dict(
            parent_order_id=order_sys_id, update_time=update_time,
            turnover=turnover, volume_traded=volume_traded, limit_price=limit_price,
            status=status, order_status=order_status, error_id=error_id, error_msg=error_msg))

    @classmethod
    def create_by_insert_req(cls, data: dict, order_id: str, trading_day: str,
                             instrument_category=InstrumentCategory.FUTURES):
        offset_flag: OffsetFlag = OFFSET_FLAG_CTP2VT[data["CombOffsetFlag"]]
        direction: Direction = DIRECTION_CTP2VT[data["Direction"]]

        return cls(data=dict(
            instrument_category=instrument_category,
            trading_day=trading_day, insert_time=int(time.time_ns()),
            offset=offset_flag, side=direction, hedge_flag=data["CombHedgeFlag"],
            order_id=order_id, order_ref_id=data["OrderRef"],
            time_condition=data["TimeCondition"], volume_condition=data["VolumeCondition"],
            account_id=data["InvestorID"], exchange_type=data["ExchangeID"],
            instrument=data["InstrumentID"], price_type=data["OrderPriceType"],
            volume=data["VolumeTotalOriginal"], limit_price=data["LimitPrice"],
            client_id=data.get("front_id")))

    @property
    def limit_price(self) -> float:
        return self.data["limit_price"]

    @property
    def volume(self) -> float:
        return self.data["volume"]

    @property
    def volume_traded(self) -> float:
        return self.data["volume_traded"]

    @property
    def turnover(self) -> float:
        return self.data["turnover"]

    @property
    def parent_order_id(self) -> str:
        return self.data.get("parent_order_id")

    @property
    def error_id(self) -> int:
        return self.data.get("error_id", 0)

    @property
    def error_msg(self) -> str:
        return self.data.get("error_msg", "")

    @property
    def instrument_type(self) -> str:
        return self.data["instrument_type"]

    @property
    def client_id(self):
        return self.data["client_id"]

    @property
    def id(self):
        return self.data["id"]