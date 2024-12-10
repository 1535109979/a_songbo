import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas
import pandas as pd

from a_songbo.asongbo_backtest.backtesting.staretegys.breakout_strategy import BreakoutStrategy
from a_songbo.asongbo_backtest.backtesting.staretegys.cover_strategy import CoverStrategy
from a_songbo.asongbo_backtest.backtesting.trade_process import TradeProcess

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)


class Backtestor:
    def __init__(self):
        self.start_time = '2024-01-01 00:00:00'

        # self.instrument_config = {
        #     'instrument': 'ondousdt', 'cash': 200,
        #     'windows': 430, 'roll_mean_period': 200, 'interval_period': 710,
        #     'strategy_name': ['breakout', 'bid'], 'open_direction': 'LONG',
        # }

        self.instrument_config = {
            'instrument': 'rlcusdt', 'cash': 200,
            'windows': 400, 'roll_mean_period': 120, 'interval_period': 860,
            'strategy_name': ['breakout','bid'], 'open_direction': 'LONG',
        }

        cover_config = {'cover_count': 0,'stop_profit_rate':1.3,'peak': 0, 'tough': 0,
            'cover_multi_list': [2, 4, 8, 16, 32, 64],
            # 'cover_decline_list': [4, 5, 6, 7, 8, 9],}
            'cover_decline_list': [5, 6, 7, 8, 9, 10],}
            # 'cover_decline_list': [6, 6, 6, 6, 6, 6],}
            # 'cover_decline_list': [2, 2, 2, 2, 2, 2],}

        self.instrument_config.update(cover_config)

        self.strategy_maps = []
        self.trade_process = TradeProcess(self)

    def start(self):
        self.data = self.load_data(self.instrument_config['instrument'])
        self.load_strategy()

        self.run_breaktest()

        self.trade_process.cal_index()

    def run_breaktest(self):
        for quote in self.data:
            close = quote.close
            self.trade_process.update_by_close(close)

            for s in self.strategy_maps:
                s.cal_singal(quote)



    def load_strategy(self):
        for s in self.instrument_config['strategy_name']:
            if s == 'breakout':
                self.strategy_maps.append(BreakoutStrategy(self))

            if s == 'bid':
                self.strategy_maps.append(CoverStrategy(self))

    def load_data(self, symbol):
        db_fp = '/Users/edy/byt_pub/a_songbo/binance_client/backtest/binance_quote_data.db'
        with sqlite3.connect(db_fp) as conn:
            df = pd.read_sql(
                f'select * from future_{symbol} where start_time >= "{self.start_time}" order by start_time DESC',
                conn)

            df = df.sort_values(by='start_time').reset_index(drop=True)
            df['symbol'] = symbol

        return [df.loc[x] for x in range(len(df)-1)]

    @property
    def position(self):
        return self.trade_process.position


if __name__ == '__main__':
    Backtestor().start()

