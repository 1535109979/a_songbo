from dataclasses import dataclass, field
from typing import List

from a_songbo.vn.books.instrument_book import InstrumentBook
from a_songbo.vn.books.rtn_trade import RtnTrade
from a_songbo.vn.enums.exchange_enum import Direction, ExchangeType, OffsetFlag
from a_songbo.vn.util import type_util
from a_songbo.vn.util.lock import instance_synchronized


@dataclass
class InstrumentPosition:
    """ 合约单方向持仓信息 """

    direction: Direction
    exchange_type: ExchangeType
    instrument: str

    yd: float = 0       # 昨仓数量
    td: float = 0       # 今仓数量
    locked: float = 0   # 锁仓数量
    volume: float = 0   # 总持仓数量

    open_volume: float = 0  # 建仓以来的总开仓数量 (从建仓开始计算开仓数量, 不计算平仓数量, 清仓后重置为0)
    open_amount: float = 0  # 当前持仓的开仓数额 (用于计算官方展示的开仓均价)
    cost_amount: float = 0  # 持仓成本数额 (数额 = 数量 * 价格 * 合约乘数)

    cost: float = 0      # 持仓成本价
    avg: float = 0       # 实际开仓均价 (从建仓开始计算开仓的均价, 不受部分平仓和交易所结算影响)
    open_avg: float = 0  # 交易所开仓均价, 以交易所逐笔盈亏算法为准

    margin: float = 0   # 占用保证金
    pos_days: int = 0  # 持仓天数
    pnl: float = 0      # 持仓盈亏

    # 开仓记录: [ {"Volume": 开仓数量, "OpenPrice": 成交价, "CloseVolume": 部分平仓数量} ]
    open_trade_datas: List[dict] = field(default_factory=list)

    # 用于区分持仓对象是否只是默认创建但没有数据更新的
    default: bool = True

    def __str__(self):
        return f"{self.instrument} {self.direction.value} " \
               f"open_avg={self.open_avg} avg={self.avg} cost={self.cost} " \
               f"open_volume={self.open_volume} volume={self.volume} yd={self.yd} td={self.td} " \
               f"locked={self.locked} margin={self.margin} " \
               f"cost_amount={self.cost_amount} open_amount={self.open_amount} " \
               f"pnl={self.pnl} pos_days={self.pos_days} otc={len(self.open_trade_datas)}"
    __repr__ = __str__

    @property
    def sellable(self) -> float:
        """ 可平仓数量 """
        return self.volume - self.locked

    def __post_init__(self):
        # [ position data list ]
        self.datas: List[dict] = list()

        # [ position trade detail ]
        self.details: List[dict] = list()

    def append_data(self, data: dict):
        self.datas.append(data)

    def append_detail(self, data: dict):
        self.details.append(data)

    def has_pos(self) -> bool:
        return self.volume > 0

    @instance_synchronized
    def update_by_datas(self, instrument_book: InstrumentBook, reqid=None, clear=True) -> bool:
        """ 根据 datas 计算持仓信息 """
        data_list = [d for d in self.datas if not reqid or reqid == d["reqid"]]
        if not data_list:
            return False
        self.default = False

        # 清理集合
        if clear:
            self.datas.clear()

        # 计算持仓信息
        tot_pos_volume = tot_yd = tot_locked = 0
        tot_margin = tot_pnl = tot_position_amount = pos_days = 0
        is_shfe_ine: bool = instrument_book.exchange_type in (ExchangeType.SHFE, ExchangeType.INE)
        for d in data_list:
            # 计算持仓数量
            pos_volume = d["Position"]
            tot_pos_volume += pos_volume

            if is_shfe_ine:
                # 对于上期所昨仓需要特殊处理
                if d.get("YdPosition") and not d.get("TodayPosition"):
                    tot_yd += pos_volume
            else:
                # 对于其他交易所昨仓的计算
                tot_yd += pos_volume - d["TodayPosition"]

            # 更新仓位冻结数量
            if Direction.LONG == self.direction:
                tot_locked += d["ShortFrozen"]
            else:
                tot_locked += d["LongFrozen"]

            if pos_volume:
                tot_position_amount += d["PositionCost"]  # 当前持仓的开仓数额
                tot_margin += d["ExchangeMargin"]  # 占用保证金
                tot_pnl += d["PositionProfit"]  # 持仓盈亏
                pos_days = max(pos_days, int(d["PositionDate"]))  # 持仓天数

        self.volume = tot_pos_volume
        self.td = tot_pos_volume - tot_yd
        self.yd = tot_yd
        self.locked = tot_locked
        self.pnl = tot_pnl
        self.pos_days = pos_days

        if tot_pos_volume:
            # 占用保证金 (期权没有保证金属性, 这里使用数额代替)
            self.margin = type_util.get_precision_number(
                number=tot_margin or tot_position_amount, precision=2)

            self.open_amount = type_util.get_precision_number(
                number=tot_position_amount, precision=2)

            # 交易所逐笔盈亏计算的开仓均价
            self.open_avg = type_util.get_precision_number(
                number=tot_position_amount / (tot_pos_volume * instrument_book.size),
                precision=2)
        else:
            self.avg = self.cost = self.open_avg = 0
            self.open_volume = self.open_amount = self.cost_amount = 0
            self.margin = self.pos_days = self.pnl = 0
        return True

    @instance_synchronized
    def update_by_details(self, instrument_book: InstrumentBook, reqid=None, clear=True) -> bool:
        """ 根据 details 计算持仓信息 """
        data_list = [d for d in self.details if not reqid or reqid == d["reqid"]]
        if not data_list:
            return False
        self.default = False

        # 清理集合
        if clear:
            self.details.clear()

        # 将持仓明细作为开仓记录 (按开仓日期和成交编号升序排序)
        self.open_trade_datas = data_list = sorted(
            data_list, reverse=False,
            key=lambda d: (int(d["OpenDate"]), int(str(d["TradeID"]).strip())))

        # 根据每笔开仓数量和成交价格计算开仓均价
        tot_pos_volume = tot_open_volume = tot_turnover = tot_cost_amount = tot_margin = 0
        for d in data_list:
            # 持仓数量
            pos_volume = d["Volume"]
            tot_pos_volume += pos_volume

            # 持仓数量等于0则表示是已经清仓的持仓记录, 不需要计算入内
            if not tot_pos_volume:
                continue

            # 开仓数量 = 持仓数量 + 已平仓数量
            open_volume = pos_volume + d["CloseVolume"]
            tot_open_volume += open_volume

            # 开仓成交金额
            open_turnover = open_volume * d["OpenPrice"]
            tot_turnover += open_turnover

            # 持仓成本数额 = 开仓数额 - 已平仓数额
            tot_cost_amount += (open_turnover * instrument_book.size - d['CloseAmount'])

            # 保证金
            tot_margin += d["Margin"]

        # 开仓总数量, 不同于持仓数量, 这个值包含已经部分平仓的数量
        self.open_volume = tot_open_volume

        if tot_pos_volume:
            self.avg = type_util.get_precision_number(
                number=(tot_turnover / tot_open_volume), precision=2)
            self.cost = type_util.get_precision_number(
                number=(tot_cost_amount / tot_pos_volume / instrument_book.size),
                precision=2)

            self.cost_amount = type_util.get_precision_number(
                number=tot_cost_amount, precision=2)

            # 期权不需要再计算保证金
            if tot_margin:
                self.margin = type_util.get_precision_number(
                    number=tot_margin, precision=2)
        else:
            self.avg = self.cost = self.open_avg = 0
            self.open_volume = self.open_amount = self.cost_amount = 0
            self.margin = self.pos_days = self.pnl = 0
        return True

    @instance_synchronized
    def update_by_trade_rtn(self, rtn: RtnTrade, instrument_book: "InstrumentBook"):
        """
        @param rtn: 成交回报
        @param instrument_book: 合约属性字典
        """
        self.default = False
        old_avg = self.avg
        old_open_volume = self.open_volume

        # 成交额、成交数额
        trade_amount = rtn.turnover * instrument_book.size

        # 保证金变化
        offset_value: int = OffsetFlag.get_offset_side(offset_flag=rtn.offset_flag)
        margin_ratio = instrument_book.get_margin_ratio(self.direction)
        rtn.margin = type_util.get_precision_number(
            number=offset_value * trade_amount * margin_ratio,
            precision=2)

        if OffsetFlag.OPEN == rtn.offset_flag:
            self.td += rtn.volume
            self.open_volume += rtn.volume
            self.open_amount += trade_amount

            # 计算开仓均价 (开仓均价不受部分平仓影响)
            self.avg = type_util.get_precision_number(
                number=(rtn.turnover + old_avg * old_open_volume) / self.open_volume,
                precision=2)

            # 记录开仓数据
            self.open_trade_datas.append(
                {"Volume": rtn.volume, "OpenPrice": rtn.price, "CloseVolume": 0})
        else:
            if OffsetFlag.CLOSE_TODAY == rtn.offset_flag:
                self.td -= rtn.volume
            elif OffsetFlag.CLOSE_YESTERDAY == rtn.offset_flag:
                self.yd -= rtn.volume
            else:
                if instrument_book.exchange_type in (ExchangeType.SHFE, ExchangeType.INE):
                    self.yd -= rtn.volume
                else:
                    self.td -= rtn.volume
                    if self.td < 0:
                        self.yd += self.td
                        self.td = 0

            # 部分平仓时, 逐笔计算
            if self.volume > rtn.volume:
                trade_volume = rtn.volume
                index = 0
                while trade_volume > 0 and index < len(self.open_trade_datas):
                    d = self.open_trade_datas[index]
                    index += 1
                    d_volume = d["Volume"]
                    if d_volume:
                        t_volume = min(d_volume, trade_volume)
                        d["CloseVolume"] += t_volume
                        d["Volume"] -= t_volume
                        trade_volume -= t_volume

                        self.open_amount -= t_volume * instrument_book.size * d["OpenPrice"]
                        rtn.profit = (t_volume * instrument_book.size *
                                      (rtn.price - d["OpenPrice"]) * self.direction.value)
                        rtn.margin += rtn.profit * margin_ratio

        # 持仓数量 = 今仓 + 昨仓
        self.volume = self.td + self.yd

        if not self.volume:
            self.avg = self.cost = self.open_avg = 0
            self.open_volume = self.open_amount = self.cost_amount = 0
            self.margin = self.pos_days = self.pnl = 0
        else:
            # 保证金
            self.margin = type_util.get_precision_number(
                number=self.margin + rtn.margin, precision=2)

            # 持仓成本
            self.cost_amount += (offset_value * trade_amount)
            self.cost = type_util.get_precision_number(
                number=self.cost_amount / self.volume / instrument_book.size,
                precision=2)

            # 交易所开仓均价
            self.open_avg = type_util.get_precision_number(
                number=self.open_amount / self.volume / instrument_book.size,
                precision=2)

            self.open_amount = type_util.get_precision_number(
                number=self.open_amount, precision=2)
            self.cost_amount = type_util.get_precision_number(
                number=self.cost_amount, precision=2)


@dataclass
class InstrumentPositionBook:
    """ 合约多空方向持仓信息 """

    vt_symbol: str

    def __post_init__(self):
        self.instrument, exchange_type = self.vt_symbol.split(".")
        self.exchange_type: ExchangeType = ExchangeType.get_by_value(exchange_type)

        # 多空方向持仓信息
        self.long_position = InstrumentPosition(
            direction=Direction.LONG, instrument=self.instrument, exchange_type=self.exchange_type)
        self.short_position = InstrumentPosition(
            direction=Direction.SHORT, instrument=self.instrument, exchange_type=self.exchange_type)

    def get_by_direction(self, direction: Direction) -> InstrumentPosition:
        """ 获取指定方向的持仓信息对象 """
        return self.short_position if Direction.is_equals(Direction.SHORT, direction) \
            else self.long_position