from dataclasses import dataclass, field

from a_songbo.vn.enums.exchange_enum import ExchangeType, ProductClass, Direction
from a_songbo.vn.util import type_util
from a_songbo.vn.util.lock import instance_synchronized


@dataclass
class InstrumentBook:
    """ 合约属性字典 """

    # 合约代码.交易所
    vt_symbol: str

    data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.instrument: str = self.data.get("InstrumentID")
        self.instrument_type: str = self.data.get("ProductID")
        self.product_class: str = self.data.get("product_class", ProductClass.F)
        self.exchange_type: ExchangeType = ExchangeType.get_by_value(self.data.get("ExchangeID"))

        self.contract_multiplier: float = self.data.get("VolumeMultiple")
        self.min_price_step: float = self.data.get("PriceTick")

        self.min_volume_value: float = self.data.get("MinMarketOrderVolume", 1)
        self.max_volume_value: float = self.data.get("MaxMarketOrderVolume", 1)

        self.long_margin_ratio: float = type_util.get_precision_number(
            number=type_util.valid_inf(value=self.data.get("LongMarginRatio"), default=1),
            precision=2, default=1)
        self.short_margin_ratio: float = type_util.get_precision_number(
            number=type_util.valid_inf(value=self.data.get("ShortMarginRatio"), default=1),
            precision=2, default=1)

    @instance_synchronized
    def update_data(self, data: dict):
        self.data.update(data)
        self.__post_init__()

    @property
    def size(self) -> float:
        return self.contract_multiplier

    def get_margin_ratio(self, direction: Direction) -> float:
        return self.short_margin_ratio if Direction.is_equals(Direction.SHORT, direction) \
            else self.long_margin_ratio

    def cal_margin(self, volume: float, price: float, direction: Direction, precision: int = None) \
            -> float:
        """ 计算占用的保证金 """
        return type_util.get_precision_number(
            number=(price * volume * self.size * self.get_margin_ratio(direction)),
            precision=2 if precision is None else precision)
