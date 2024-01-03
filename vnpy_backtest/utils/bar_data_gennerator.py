import re
from dataclasses import dataclass
from datetime import datetime, time


@dataclass
class TickData:
    symbol: str
    datetime: datetime

    turnover: float = 0
    volume: float = 0
    open_interest: float = 0
    limit_up: float = 0
    limit_down: float = 0

    open: float = 0
    high: float = 0
    low: float = 0
    last: float = 0

    bid_price_1: float = 0
    bid_price_2: float = 0
    bid_price_3: float = 0
    bid_price_4: float = 0
    bid_price_5: float = 0

    ask_price_1: float = 0
    ask_price_2: float = 0
    ask_price_3: float = 0
    ask_price_4: float = 0
    ask_price_5: float = 0

    bid_volume_1: float = 0
    bid_volume_2: float = 0
    bid_volume_3: float = 0
    bid_volume_4: float = 0
    bid_volume_5: float = 0

    ask_volume_1: float = 0
    ask_volume_2: float = 0
    ask_volume_3: float = 0
    ask_volume_4: float = 0
    ask_volume_5: float = 0


@dataclass
class BarData:
    symbol: str
    datetime: datetime

    start_volume: float = 0
    volume: float = 0
    start_turnover: float = 0
    turnover: float = 0
    open_interest: float = 0

    open: float = 0
    high: float = 0
    low: float = 0
    close: float = 0


class BarGen:
    def __init__(self, interval='m', on_bar=None):
        self.interval = interval
        self.on_bar = on_bar
        self.interval_type_second_map = {'s': 1, 'm': 60, 'h': 3600, 'M': 60, 'H': 3600}

        self.time_interval = None
        self.last_time = None
        self.last_tick = None
        self.interval_type = None

        self.bar = None

        self.set_time_interval()

    def on_tick(self, tick: TickData):
        # print(tick.datetime)
        if not self.in_trading_time(tick.datetime):
            return

        if not self.last_time:
            self.last_time = tick.datetime.replace(microsecond=0, second=0)
            self.bar = self.create_bar(tick)
        else:
            if self.need_change_time(tick.datetime):
                self.on_bar(self.bar)
                self.last_time = tick.datetime.replace(microsecond=0, second=0)
                self.bar = self.create_bar(tick)
                # quit()
            else:
                self.update_bar(tick)

    def create_bar(self, tick):
        return BarData(symbol=tick.symbol, datetime=tick.datetime.replace(microsecond=0, second=0), start_volume=tick.volume,
                       start_turnover=tick.turnover, open_interest=tick.open_interest,
                       open=tick.last, high=tick.last, low=tick.last, close=tick.last
                        )

    def update_bar(self, tick):
        self.bar.volume = tick.volume - self.bar.start_volume
        self.bar.turnover = tick.turnover - self.bar.start_turnover
        self.bar.close = tick.last
        if tick.high > self.bar.high:
            self.bar.high = tick.high
        if tick.low < self.bar.low:
            self.bar.low = tick.low

        # quit()

    def need_change_time(self, tick_time):
        return (tick_time - self.last_time).seconds >= self.time_interval

    def set_time_interval(self):
        if re.match('[0-9]+', self.interval):
            interval_multi = int(re.match('[0-9]+', self.interval).group())
        else:
            interval_multi = 1
        self.interval_type = re.findall('([a-zA-Z]+)', self.interval)[0]
        interval_base = self.interval_type_second_map.get(self.interval_type)

        self.time_interval = interval_multi * interval_base

    def in_trading_time(self, tick_time: datetime):
        if (((time(9, 0, 0) <= tick_time.time() <= time(10, 15, 0) or
                time(10, 15, 0) <= tick_time.time() <= time(11, 30, 0)) or
                time(13, 0, 0) <= tick_time.time() <= time(15, 00, 0)) or
                time(21, 0, 0) <= tick_time.time() <= time(23, 59, 59)):
            return True
        return False