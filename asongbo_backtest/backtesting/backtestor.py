import copy
import sqlite3

import pandas
import pandas as pd
from sqlalchemy import create_engine, text

from a_songbo.asongbo_backtest.backtesting.staretegys.breakout_strategy import BreakoutStrategy
from a_songbo.asongbo_backtest.backtesting.staretegys.cover_strategy import CoverStrategy
from a_songbo.asongbo_backtest.backtesting.staretegys.open_strategy import OpenStrategy
from a_songbo.asongbo_backtest.backtesting.staretegys.ut_bot_alets import UtBotAletStrategy
from a_songbo.asongbo_backtest.backtesting.trade_process import TradeProcess

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)


class Backtestor:
    def __init__(self):
        self.start_time = '2025-01-01 00:00:00'
        self.source_type = 'CRYPTO'    # CRYPTO  STOCK
        self.strategy_maps = []
        self.daily_settlement = False


    def start(self):
        instrument_configs = [
            {'instrument': 'ltcusdt', 'windows': 550, 'roll_mean_period': 630, 'interval_period': 60, },
            {'instrument': 'eosusdt', 'windows': 390, 'roll_mean_period': 100, 'interval_period': 100, },
            # {'instrument': 'rlcusdt', 'windows': 400, 'roll_mean_period': 120, 'interval_period': 860, },
            # {'instrument': 'ondousdt', 'windows': 430, 'roll_mean_period': 200, 'interval_period': 710, },
            {'instrument': 'aevousdt', 'windows': 600, 'roll_mean_period': 350, 'interval_period': 320, },
            {'instrument': 'bandusdt', 'windows': 730, 'roll_mean_period': 540, 'interval_period': 660, },
            {'instrument': 'celrusdt', 'windows': 720, 'roll_mean_period': 610, 'interval_period': 400, },
            {'instrument': 'movrusdt', 'windows': 300, 'roll_mean_period': 300, 'interval_period': 900, },
            {'instrument': 'nfpusdt', 'windows': 390, 'roll_mean_period': 100, 'interval_period': 320, },
            {'instrument': 'portalusdt', 'windows': 600, 'roll_mean_period': 500, 'interval_period': 600, },
        ]

        cover_config = {
            'strategy_name': ['utbot'], 'open_direction': 'LONG',
            'cover_count': 0, 'stop_profit_rate': 1.3, 'peak': 0, 'tough': 0,
            'cover_multi_list': [2, 4, 8, 16, 32, 64],
            # 'cover_decline_list': [4, 5, 6, 7, 8, 9],}
            'cover_decline_list': [5, 6, 7, 8, 9, 10],}
            # 'cover_decline_list': [6, 6, 6, 6, 6, 6],}
            # 'cover_decline_list': [2, 2, 2, 2, 2, 2],}

        cover_decline_list = [
            # {'cover_decline_list': [2, 2, 2, 2, 2, 2]},
            # {'cover_decline_list': [3, 3, 3, 3, 3, 3]},
            # {'cover_decline_list': [4, 4, 4, 4, 4, 4]},
            # {'cover_decline_list': [1, 2, 3, 4, 5, 6]},
            # {'cover_decline_list': [2, 3, 4, 5, 6, 7]},
            # {'cover_decline_list': [3, 4, 5, 6, 7, 8]},
            # {'cover_decline_list': [4, 5, 6, 7, 8, 9]},
            {'cover_decline_list': [5, 6, 7, 8, 9 ,10]},
            {'cover_decline_list': [7, 8, 9 ,10, 11, 12]},
            {'cover_decline_list': [9 ,10, 11, 12, 13, 14]},
        ]

        base_config = {'instrument': 'sh600369','cover_multi_list': [2, 4, 8, 16, 32, 64, 128, 256, 512],
             'peak': 0, 'tough': 0,'cover_count': 0, 'open_direction': 'LONG',}

        # instrument_configs = [
        #     {'instrument': 'sh600369','cover_multi_list': [2, 4, 8, 16, 32, 64, 128, 256, 512],
        #      'peak': 0, 'tough': 0,'cover_count': 0, 'open_direction': 'LONG',},
        #
        # ]

        stop_profit_list = [
            {'stop_profit_rate': 1},
            {'stop_profit_rate': 1.3},
            {'stop_profit_rate': 1.7},
            {'stop_profit_rate': 2},
            # {'stop_profit_rate': 2.5},
            # {'stop_profit_rate': 3},
            # {'stop_profit_rate': 3.5},
            # {'stop_profit_rate': 4},
            # {'stop_profit_rate': 4.5},
            # {'stop_profit_rate': 5},
        ]

        # stock_list = self.get_all_stocks()
        # for stock in stock_list:
        #     base_config.update({'instrument':stock})
        #     instrument_configs.append(copy.deepcopy(base_config))


        for instrument_config in instrument_configs:
            self.instrument_config = instrument_config
            self.data = self.load_data(self.instrument_config['instrument'])

            for cover_decline_ in cover_decline_list:
                for stop_profit_ in stop_profit_list:
                    self.instrument_config.update(cover_config)
                    self.instrument_config.update(cover_decline_)
                    self.instrument_config.update(stop_profit_)
                    print(self.instrument_config)

                    self.trade_process = TradeProcess(self)
                    self.strategy_maps = []
                    self.load_strategy(self.instrument_config['strategy_name'])

                    self.run_breaktest()

                    self.trade_process.cal_index()

    def run_breaktest(self):
        for quote in self.data:
            close = quote.close
            self.trade_process.update_by_close(close)

            for s in self.strategy_maps:
                s.cal_singal(quote)

            if self.daily_settlement:
                self.trade_process.daily_settle(close)

    def load_strategy(self, strategy_name):
        for s in strategy_name:
            if s == 'breakout':
                self.strategy_maps.append(BreakoutStrategy(self))

            if s == 'open':
                self.strategy_maps.append(OpenStrategy(self))

            if s == 'bid':
                self.strategy_maps.append(CoverStrategy(self))

            if s == 'utbot':
                self.strategy_maps.append(UtBotAletStrategy(self))

    def get_all_stocks(self):
        url = 'clickhouse+http://clickhouse:CK-clickhouse@49.235.94.80:8123/md'
        engine = create_engine(url)
        sql = f"select distinct symbol from bar_daily_stock"
        df = pd.read_sql(text(sql), engine)
        return df['symbol'].to_list()

    def load_data(self, symbol):
        if self.source_type == 'CRYPTO':
            db_fp = '/Users/edy/byt_pub/a_songbo/binance_client/backtest/binance_quote_data.db'
            with sqlite3.connect(db_fp) as conn:
                df = pd.read_sql(
                    f'select * from future_{symbol} where start_time >= "{self.start_time}" order by start_time DESC',
                    conn)

                df = df.sort_values(by='start_time').reset_index(drop=True)
                df['symbol'] = symbol

            return [df.loc[x] for x in range(len(df)-1)]

        if self.source_type == 'STOCK':
            url = 'clickhouse+http://clickhouse:CK-clickhouse@49.235.94.80:8123/md'
            engine = create_engine(url)
            sql = f"select symbol, date, close from bar_daily_stock where symbol='{symbol}'"
            df = pd.read_sql(text(sql), engine)
            df.columns = ['symbol', 'start_time', 'close']
            df = df.sort_values(by='start_time').reset_index(drop=True)
            return [df.loc[x] for x in range(len(df) - 1)]

    @property
    def position(self):
        return self.trade_process.position


if __name__ == '__main__':
    Backtestor().start()

