from collections import Counter
from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd


@dataclass
class Position:
    symbol: str
    direction: str
    cost: float
    volume: float
    last_trade_price: float
    peak: float = 0
    tough: float = 0
    cover_count: int = 0

    def update_by_close(self, close):
        close = float(close)
        if not self.peak:
            self.peak = close
            return
        if not self.tough:
            self.tough = close
            return
        if close > self.peak:
            self.peak = close
        if close < self.tough:
            self.tough = close


class TradeProcess:
    def __init__(self, backtestor):
        self.backtestor = backtestor
        self.position = None
        self.account_value = 1
        self.commission = 0.0006
        self.account_value_list = []
        self.profit_rate = []
        self.trade_df = pd.DataFrame(columns=['trade_time','symbol', 'offset_flat', 'direction','cost', 'price', 'volume',
                                              'account_value', 'cover_count'])

    def update_by_close(self, close):
        if self.position:
            self.position.update_by_close(close)

    def stop_profit(self, quote_time, price, profit_rate):
        self.account_value += (profit_rate - self.commission) * self.position.volume
        self.account_value_list.append(self.account_value)

        self.trade_df.loc[len(self.trade_df)] = \
            [quote_time, self.position.symbol, 'stop_profit', self.position.direction, self.position.cost, price, self.position.volume,
             self.account_value, self.position.cover_count]

        self.position = None

    def cover_order(self,quote_time, direction, price, volume):

        self.account_value += - self.commission * volume
        self.account_value_list.append(self.account_value)

        self.position.cost = (self.position.cost * self.position.volume + price * volume) / (self.position.volume + volume)
        self.position.last_trade_price = price
        self.position.volume += volume
        self.position.cover_count += 1

        self.trade_df.loc[len(self.trade_df)] = \
            [quote_time, self.position.symbol, 'cover_order', direction, self.position.cost, price, volume,
             self.account_value, self.position.cover_count]


    def reverse(self,quote_time, symbol, dir, price, volume=1):
        if not self.position:
            self.position = Position(symbol, dir,price,volume,
                                     last_trade_price=price,peak=price,tough=price)
            self.account_value += - self.commission * volume
            self.account_value_list.append(self.account_value)

            self.trade_df.loc[len(self.trade_df)] = \
                [quote_time, self.position.symbol, 'open', dir, price, price, volume,
                 self.account_value, self.position.cover_count]

        else:
            if self.position.direction == dir:
                return
            elif self.position.direction == 'LONG' and dir == 'SHORT':
                profit_rate = price / self.position.cost - 1
            elif self.position.direction == 'SHORT' and dir == 'LONG':
                profit_rate = 1 - price / self.position.cost

            # 平仓
            self.profit_rate.append(profit_rate)
            self.account_value += (profit_rate - self.commission) * self.position.volume
            self.account_value_list.append(self.account_value)
            self.trade_df.loc[len(self.trade_df)] = \
                [quote_time, self.position.symbol,'close', self.position.direction, self.position.cost, price, volume,
                 self.account_value, self.position.cover_count]
            # 开仓
            self.position.direction = dir
            self.position.cost = price
            self.position.volume = volume
            self.position.last_trade_price = price
            self.position.peak = price
            self.position.tough = price
            self.position.cover_count = 0
            self.account_value += - self.commission * volume
            self.trade_df.loc[len(self.trade_df)] = \
                [quote_time, self.position.symbol, 'open', dir,self.position.cost, price, volume, self.account_value, self.position.cover_count]

    def cal_index(self):
        print(self.trade_df)
        cover_count = Counter(self.trade_df['cover_count'])
        print(cover_count)
        co = ''
        for k,v in cover_count.items():
            co += str(k) + ':' + str(v) + ','

        plt.title(self.backtestor.instrument_config['instrument'] + ' ' +
                  ''.join([str(x) for x in self.backtestor.instrument_config['cover_decline_list']]) +
                  ' '+ co)
        plt.plot(self.account_value_list)
        plt.show()


