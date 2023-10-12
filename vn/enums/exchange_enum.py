from enum import Enum, unique

from a_songbo.vn.util.type_util import get_iter


class BaseEnum(Enum):

    def __str__(self):
        return self.name

    def __repr__(self):
        return "%s.%s:%s" % (self.__class__.__name__, self._name_, self._value_)

    @classmethod
    def get_by_value(cls, value):
        if not value:
            return
        if isinstance(value, cls):
            return value

        v = str(value).upper()
        for s in cls.__members__.values():
            if v == str(s.value) or v == str(s.name):
                return s

    @classmethod
    def is_equals(cls, e1, e2):
        if e1 is None or e2 is None:
            return e1 is None and e2 is None
        if e1 == e2:
            return True
        return str(e1) == str(e2)

    @classmethod
    def contains(cls, e, es):
        if e is None or not es:
            return e is None and not es

        es = get_iter(es)
        for s in es:
            if str(e) == str(s):
                return True

        return False


@unique
class InstrumentCategory(BaseEnum):
    STOCK = 'S'                    # 股票
    FUTURES = "F"                  # 期货
    DIGICCY = "D"                  # 数字货币
    DIGICCY_FUTURES = 'DF'         # 数字合约

    @classmethod
    def get_base_instrument_type(cls, instrument_category):
        if cls.is_equals(cls.FUTURES, instrument_category) \
                or cls.is_equals(cls.STOCK, instrument_category):
            return "CNY"
        return "USDT"

    @classmethod
    def get_digiccy_categories(cls):
        return cls.DIGICCY, cls.DIGICCY_FUTURES


@unique
class Direction(BaseEnum):
    """多空方向"""
    LONG = 1  # 多 (持多仓)
    SHORT = -1  # 空 (持空仓)
    NET = 0  # 净 (清仓)
    BI = 2  # 锁 (双向持仓)



@unique
class ExchangeType(BaseEnum):
    """交易所"""
    CZCE = "czce"  # 郑商所
    DCE = "dce"  # 大商所
    CFFEX = "cffex"  # 中金所
    SHFE = "shfe"  # 上期所
    SSE = "sse"  # 上交所
    SZE = "sze"  # 深交所
    GFEX = "gfex"  # 广交所
    INE = "ine"  # 上能所
    CMX = "cmx"  # 纽约商品交易所 (GLN, SLN)
    IPE = "ipe"  # 伦敦国际石油交易所 (OIL, GAL)
    NYM = "nym"  # 纽约商业交易所 (CON, HON)
    CBT = "cbt"  # 芝加哥商品期货交易所 (SOC, SBC, SMC, CRC)
    NYB = "nyb"  # 纽约期货交易所 (SGN)
    BINANCE = "binance"  # 币安交易所 BINANCE
    HUOBI = "huobi"  # 火币交易所 HUOBI
    BINANCE_F = "binance_f"  # 币安交易所期货 BINANCE
    GD = "gd"  # 没有特定的交易所或在同时有多个交易所的情况时使用这个代替


@unique
class ProductClass(BaseEnum):
    """ 产品类别 """
    F = "FUTURES"                 # 期货合约
    FO = "FUTURES_OPTIONS"        # 期货合约期权
    D = "DIGICCY"                 # 数字货币
    DF = 'DIGICCY_FUTURES'        # 数字货币合约


@unique
class OrderPriceType(BaseEnum):
    """报单价格类型"""
    FAK = "fak"  # fill and kill
    FOK = "fok"  # fill or kill
    LIMIT = "limit"  # 限价单
    MARKET = "market"  # 市价单
    MARKET_QTY = "market_qty"  # 市价单，数字货币交易所会根据金额买入相应价值的
    STOP = "stop"  # 停止单
    REQ = "req"  # 询价单

    @classmethod
    def is_qty(cls, order_price_type):
        return cls.is_equals(cls.MARKET_QTY, order_price_type)


@unique
class OffsetFlag(BaseEnum):
    """开平类型"""
    NONE = ""
    OPEN = "0"  # 开
    CLOSE = "1"  # 平
    CLOSE_TODAY = "3"  # 平今
    CLOSE_YESTERDAY = "4"  # 平昨

    @classmethod
    def get_cn(cls, offset_flag, direction=None) -> str:
        if cls.is_equals(cls.OPEN, offset_flag):
            return "开"
        if cls.is_equals(cls.CLOSE, offset_flag):
            return "平"
        if cls.is_equals(cls.CLOSE_TODAY, offset_flag):
            return "平今"
        if cls.is_equals(cls.CLOSE_YESTERDAY, offset_flag):
            return "平昨"
        if cls.is_equals(cls.NONE, offset_flag) and direction:
            return "开" if Direction.is_equals(Direction.LONG, direction) else "平"
        return ""

    @classmethod
    def get_offset_side(cls, offset_flag, direction=None) -> int:
        if cls.is_equals(cls.OPEN, offset_flag):
            return 1
        elif cls.is_equals(cls.NONE, offset_flag):
            if direction:
                return 1 if Direction.is_equals(Direction.LONG, direction) else -1
            else:
                return 0
        else:
            return -1

    @classmethod
    def get_close_offset_flags(cls):
        return cls.CLOSE, cls.CLOSE_TODAY, cls.CLOSE_YESTERDAY

    @classmethod
    def is_open_by_name(cls, offset_flag, direction=None):
        if cls.is_equals(cls.OPEN, offset_flag):
            return True
        if cls.is_equals(cls.NONE, offset_flag):
            if direction and Direction.is_equals(Direction.LONG, direction):
                return True
        return False

    @classmethod
    def is_close_by_name(cls, offset_flag, direction=None):
        if cls.is_equals(cls.OPEN, offset_flag):
            return False
        if cls.is_equals(cls.NONE, offset_flag):
            if not direction or not Direction.is_equals(Direction.SHORT, direction):
                return False
        return True

    def is_close(self, direction=None):
        return self.is_close_by_name(offset_flag=self, direction=direction)


@unique
class Direction(BaseEnum):
    """多空方向"""
    LONG = 1  # 多 (持多仓)
    SHORT = -1  # 空 (持空仓)
    NET = 0  # 净 (清仓)
    BI = 2  # 锁 (双向持仓)

    @classmethod
    def get_cn(cls, direction, offset_flag=None):
        offset_flag_cn = OffsetFlag.get_cn(offset_flag) if offset_flag else ""
        if cls.is_equals(cls.LONG, direction):
            return f"{offset_flag_cn}多"
        if cls.is_equals(cls.SHORT, direction):
            return f"{offset_flag_cn}空"
        return f"多空双{offset_flag_cn}"

    @classmethod
    def get_position_direction(cls, direction, offset_flag):
        direction = Direction.get_by_value(direction)
        if OffsetFlag.is_close_by_name(offset_flag=offset_flag, direction=direction):
            return direction.get_opposite_direction()
        return direction

    def get_value(self):
        return self.value

    def is_bi_or_net(self):
        return self == self.BI or self == self.NET

    def contains_direction(self, direction):
        if self == self.BI or self == self.NET:
            return True
        return self.is_equals(self, direction)

    def get_tradable_directions(self):
        if self.is_bi_or_net():
            return Direction.LONG, Direction.SHORT
        else:
            return self,

    def get_opposite_direction(self):
        if self.LONG == self:
            return self.SHORT
        elif self.SHORT == self:
            return self.LONG
        return self

@unique
class OrderStatus(BaseEnum):
    """报单状态"""
    UNKNOWN = -1     # 未知状态
    # 最终状态
    ALL_TRADED = 0   # 全部成交
    PART_TRADED = 2  # 部分成交
    NO_TRADE = 4     # 全部未成交
    ERROR = 6        # 报单错误全部未成交

    def is_completed(self):
        """是否是最终状态"""
        return self.UNKNOWN != self

    def is_success_completed(self):
        return self.ALL_TRADED == self or self.PART_TRADED == self