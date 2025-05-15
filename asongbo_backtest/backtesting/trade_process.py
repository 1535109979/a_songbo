import csv
from collections import Counter
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress


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
    settle_price: float = 0

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
        self.commission = 0.0006
        self.account_value = 1
        self.account_value_list = []
        self.profit_rate = []
        self.trade_df = pd.DataFrame(columns=['trade_time','symbol', 'offset_flat', 'direction','cost', 'price', 'volume',
                                              'account_value', 'cover_count'])

    def update_by_close(self, close):
        if self.position:
            self.position.update_by_close(close)

    def daily_settle(self, close):
        if self.position:
            if close != self.position.settle_price and self.position.direction == 'LONG':
                profit_rate = close / self.position.settle_price - 1
                self.account_value += profit_rate * self.position.volume
                self.account_value_list.append(self.account_value)
                self.position.settle_price = close
                self.position.cost = close


    def stop_profit(self, quote_time, price, profit_rate):
        self.account_value += (profit_rate - self.commission) * self.position.volume
        self.account_value_list.append(self.account_value)

        self.trade_df.loc[len(self.trade_df)] = \
            [quote_time, self.position.symbol, 'stop_profit', self.position.direction, self.position.cost, price, self.position.volume,
             self.account_value, 0]

        self.position = None

    def open(self,quote_time, symbol, direc, price, volume=1):
        if not self.position:
            self.position = Position(symbol, direc,price,volume,
                                     last_trade_price=price,peak=price,tough=price, settle_price=price)
            self.account_value += - self.commission * volume
            self.account_value_list.append(self.account_value)

            self.trade_df.loc[len(self.trade_df)] = \
                [quote_time, self.position.symbol, 'open', direc, price, price, volume,
                 self.account_value, 0]

    def buy(self, quote, volume=1):
        if not self.position:
            self.position = Position(quote.symbol, 'LONG', float(quote.close), volume,
                                     last_trade_price=float(quote.close), peak=float(quote.close),
                                     tough=float(quote.close), settle_price=float(quote.close))
            self.account_value += - self.commission * volume
            self.account_value_list.append(self.account_value)
            self.trade_df.loc[len(self.trade_df)] = \
                [quote.start_time, self.position.symbol, 'open', 'LONG', float(quote.close), float(quote.close), volume,
                 self.account_value, 0]

    def sell(self, quote):
        pass

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
                 self.account_value, 0]

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
                 self.account_value, 0]
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
                [quote_time, self.position.symbol, 'open', dir,self.position.cost, price, volume, self.account_value, 0]

    def cal_index(self):
        # print(self.trade_df)

        trade_times = (self.trade_df['offset_flat'] == 'open').sum()
        cover_count = Counter(self.trade_df['cover_count'])
        # print(cover_count)

        max_count = max(cover_count.keys())
        max_value = 2 ** max_count *2 -1

        co = ''
        for k,v in cover_count.items():
            co += str(k) + ':' + str(v) + ','

        instrument = self.backtestor.instrument_config['instrument']
        stop_profit_rate = self.backtestor.instrument_config['stop_profit_rate']

        cover_config = ''.join([str(x) for x in self.backtestor.instrument_config['cover_decline_list']])

        # y_fit, residuals = self.line_fit(self.account_value_list)
        # max_drawdown = self.calculate_max_drawdown(self.account_value_list)
        plt_list = [ x / max_value for x in self.account_value_list]
        plt.plot(self.account_value_list)
        # plt.plot(y_fit)
        # plt.title(f"{instrument} {cover_config} {co}\nresiduals: {residuals} max_drawdown: {max_drawdown}")
        plt.title(f"{instrument} {trade_times} {cover_config} {stop_profit_rate}\n {co}")

        plt.savefig(f'result/{instrument}_{cover_config}_{stop_profit_rate}.jpg')
        plt.clf()
        # plt.show()

        ana_return = plt_list[-1] / len(self.backtestor.data) * 240

        with open('value_result.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([instrument,cover_config,stop_profit_rate,max_count,max_value,trade_times,
                             self.account_value_list[-1],ana_return])  # 写入一行数据

    def line_fit(self,value_list):
        x = np.arange(len(value_list))
        y = np.array(value_list)
        slope, intercept, r_value, p_value, std_err = linregress(x, y)

        # 计算拟合值
        y_fit = slope * x + intercept

        # 计算残差
        residuals = y - y_fit

        return y_fit, round(np.sum(np.abs(residuals))/ len(value_list), 4)

    def calculate_max_drawdown(self, account_value_list):
        # 将账户价值列表转换为 numpy 数组
        values = np.array(account_value_list)
        # 计算累积最大值
        cumulative_max = np.maximum.accumulate(values)
        # 计算每个时间点的回撤
        drawdowns = (cumulative_max - values) / cumulative_max
        # 最大回撤是所有回撤中的最大值
        max_drawdown = np.max(drawdowns)

        return round(max_drawdown, 4)

