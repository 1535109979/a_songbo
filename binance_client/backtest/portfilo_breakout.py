import sqlite3
import time
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt
import numpy as np
import pandas
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from sqlalchemy import create_engine, text

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)


class AddSymbol:
    def __init__(self, portfilo):
        self.df = None
        self.portfilo = portfilo
        self.df_trade = portfilo.df_trade
        self.symbol = 'ETHUSDT'

        self.position = None
        self.commision = 0.0007

        self.read_db()

    def read_db(self):
        with sqlite3.connect('binance_quote_data.db') as conn:
            df = pd.read_sql(
                f'select * from future_{self.symbol} where start_time >= "{self.portfilo.start_time}" order by start_time DESC',
                conn)
            df = df.set_index('start_time')
            df = df[~df.index.duplicated(keep='first')]
            df = df.drop_duplicates()
        self.df = df

    def on_quote(self, date, position_flag):
        if date in self.df.index:
            latest_price = float(self.df.loc[date].close)
        else:
            return

        if not self.position:
            if not position_flag:
                return
            else:
                self.position = (position_flag, latest_price)
                self.portfilo.account_value += -self.commision
                self.df_trade.loc[len(self.df_trade)] = [date, self.symbol, 'open', position_flag, latest_price,
                                                         self.portfilo.account_value]
        else:
            change_flag = position_flag - self.position[0]
            if change_flag:
                profit_rate = self.position[0] * (latest_price / self.position[1] - 1)
                self.portfilo.account_value += profit_rate - self.commision
                self.df_trade.loc[len(self.df_trade)] = [date, self.symbol, 'change', change_flag, latest_price,
                                                         self.portfilo.account_value]

                self.position = (position_flag, latest_price)


class SymbolProcess:
    def __init__(self, portfilo, config):
        self.portfilo = portfilo
        self.account_value_muli = 1 / self.portfilo.symbol_num
        self.df_trade = portfilo.df_trade
        self.df = None
        self.config = config
        self.symbol = self.config["symbol"]
        self.step_price = float(portfilo.min_price_step_map.get(self.symbol))

        self.window = self.config["window"]
        self.rolling_window = self.config["rolling_window"]
        self.period = self.config["period"]
        self.min_save_window = max(self.window, self.period * 2 + self.rolling_window)
        self.stop_loss_rate = 0.1
        self.commision = 0.0007

        self.am = []
        self.roll_mean_list = []
        self.last_n_min = self.last_n_max = None

        self.symbol_account_value = 1
        self.df = None

        self.position = None

        self.read_db()

    def read_db(self):
        with sqlite3.connect('binance_quote_data.db') as conn:
            df = pd.read_sql(
                f'select * from future_{self.config["symbol"]} where start_time >= "{self.portfilo.start_time}" order by start_time DESC', conn)
            df = df.set_index('start_time')
            df = df[~df.index.duplicated(keep='first')]

        self.df = df

    def on_quote(self, date):
        if date in self.df.index:
            latest_price = float(self.df.loc[date].close)

            if len(self.am) < self.min_save_window:
                self.am.append(latest_price)
                if len(self.am) >= self.rolling_window:
                    roll_mean = round(sum([float(x) for x in self.am[-self.rolling_window:]]) / self.rolling_window,
                                      8)
                    self.roll_mean_list.append(roll_mean)
                return

            self.last_n_max = max(self.am[-self.window:])
            self.last_n_min = min(self.am[-self.window:])

            self.am.append(latest_price)
            self.am = self.am[-self.min_save_window:]

            roll_mean = round(sum([float(x) for x in self.am[-self.rolling_window:]]) / self.rolling_window, 8)
            self.roll_mean_list.append(roll_mean)
            self.roll_mean_list = self.roll_mean_list[-self.period * 2:]

            if self.position:
                flag = None
                if self.position[0] == 'long':
                    rate = latest_price / self.position[1] - 1
                    flag = 'long'

                    if latest_price > self.roll_mean_list[-self.period] > self.roll_mean_list[- 2 * self.period]:
                        return

                elif self.position[0] == 'short':
                    rate = 1 - latest_price / self.position[1]
                    flag = 'short'

                    if latest_price < self.roll_mean_list[-self.period] < self.roll_mean_list[- 2 * self.period]:
                        return

                if rate < -self.stop_loss_rate:
                    self.position = None
                    self.portfilo.account_value += self.account_value_muli * (rate - 0.0002)
                    self.symbol_account_value += self.account_value_muli * (rate - 0.0002)

                    self.df_trade.loc[len(self.df_trade)] = [date, self.symbol, 'stop_close', flag, latest_price, self.portfilo.account_value]
                    return

            if latest_price < self.last_n_min:
                if not self.position:
                    self.position = ('long', latest_price)
                    self.portfilo.account_value += self.account_value_muli * (-self.commision)
                    self.symbol_account_value += self.account_value_muli * (-self.commision)
                    self.df_trade.loc[len(self.df_trade)] = [date, self.symbol, 'open', 'long', latest_price, self.portfilo.account_value]
                else:
                    if self.position[0] == 'short':
                        self.portfilo.account_value += self.account_value_muli * (1 - (latest_price + self.step_price) / (self.position[1]) - self.commision)
                        self.symbol_account_value += self.account_value_muli * (1 - (latest_price + self.step_price) / (self.position[1]) - self.commision)
                        self.df_trade.loc[len(self.df_trade)] = [date, self.symbol, 'close', 'short', latest_price, self.portfilo.account_value]

                        self.position = ('long', latest_price)
                        self.portfilo.account_value -= self.account_value_muli * (self.commision)
                        self.symbol_account_value += self.account_value_muli * (-self.commision)
                        self.df_trade.loc[len(self.df_trade)] = [date, self.symbol, 'open', 'long', latest_price, self.portfilo.account_value]
            elif latest_price > self.last_n_max:
                if not self.position:
                    self.position = ('short', latest_price)
                    self.portfilo.account_value += self.account_value_muli * (-self.commision)
                    self.symbol_account_value += self.account_value_muli * (-self.commision)

                    self.df_trade.loc[len(self.df_trade)] = [date, self.symbol, 'open', 'short', latest_price, self.portfilo.account_value]
                else:
                    if self.position[0] == 'long':
                        self.portfilo.account_value += self.account_value_muli * ((latest_price - self.step_price) / (self.position[1]) - 1 - self.commision)
                        self.symbol_account_value += self.account_value_muli * ((latest_price - self.step_price) / (self.position[1]) - 1 - self.commision)
                        self.df_trade.loc[len(self.df_trade)] = [date, self.symbol, 'close', 'long', latest_price, self.portfilo.account_value]

                        self.position = ('short', latest_price)
                        self.portfilo.account_value -= self.account_value_muli * (self.commision)

                        self.symbol_account_value += self.account_value_muli * (-self.commision)
                        self.df_trade.loc[len(self.df_trade)] = [date, self.symbol, 'open', 'short', latest_price, self.portfilo.account_value]


class BreakOutPortfilo:
    def __init__(self, choose_symbol=''):
        self.choose_symbol = choose_symbol
        self.date = set()
        self.symbol_process_map = {}
        self.account_value = 1
        self.account_value_list = []
        self.start_time = '2024-01-01 00:00:00'
        self.df_trade = pd.DataFrame(columns=['time', 'symbol', 'offset', 'dir', 'close', 'account_value'])

        self.min_price_step_map = self.read_step_price()

        self.symbol_num = None
        self.load_symbols_configs()
        self.is_add_symbol = False
        if self.is_add_symbol:
            self.add_symbol = AddSymbol(self)

    def load_symbols_configs(self):
        # self.symbol_configs_data={
        #     'EOSUSDT': {"symbol": "EOSUSDT", "window": 400, "rolling_window": 200, "period": 120},
        #     'LTCUSDT': {"symbol": "LTCUSDT", "window": 550, "rolling_window": 550, "period": 100},
        #     'AEVOUSDT': {"symbol": "AEVOUSDT", "window": 600, "rolling_window": 350, "period": 320},
        #     'APEUSDT': {"symbol": "APEUSDT", "window": 700, "rolling_window": 600, "period": 600},
        #     'BANDUSDT': {"symbol": "BANDUSDT", "window": 700, "rolling_window": 600, "period": 500},
        #     'CELRUSDT': {"symbol": "CELRUSDT", "window": 700, "rolling_window": 600, "period": 400},
        #     'ONDOUSDT': {"symbol": "ONDOUSDT", "window": 400, "rolling_window": 200, "period": 700},
        #     'NFPUSDT': {"symbol": "NFPUSDT", "window": 400, "rolling_window": 200, "period": 300},
        #     'PORTALUSDT': {"symbol": "PORTALUSDT", "window": 600, "rolling_window": 500, "period": 600},
        #     'RLCUSDT': {"symbol": "RLCUSDT", "window": 400, "rolling_window": 200, "period": 800},
        # }

        self.symbol_configs_data={
            'EOSUSDT': {"symbol": "EOSUSDT", "window": 390, "rolling_window": 100, "period": 100},
            'LTCUSDT': {"symbol": "LTCUSDT", "window": 550, "rolling_window": 630, "period": 60},
            'AEVOUSDT': {"symbol": "AEVOUSDT", "window": 600, "rolling_window": 350, "period": 320},
            'APEUSDT': {"symbol": "APEUSDT", "window": 720, "rolling_window": 540, "period": 660},
            'BANDUSDT': {"symbol": "BANDUSDT", "window": 730, "rolling_window": 520, "period": 545},
            'CELRUSDT': {"symbol": "CELRUSDT", "window": 720, "rolling_window": 610, "period": 400},
            'ONDOUSDT': {"symbol": "ONDOUSDT", "window": 430, "rolling_window": 200, "period": 710},
            'NFPUSDT': {"symbol": "NFPUSDT", "window": 390, "rolling_window": 100, "period": 320},
            'PORTALUSDT': {"symbol": "PORTALUSDT", "window": 600, "rolling_window": 500, "period": 600},
            'RLCUSDT': {"symbol": "RLCUSDT", "window": 400, "rolling_window": 120, "period": 860},
        }

        if not self.choose_symbol:
            self.symbol_configs = self.symbol_configs_data
        else:
            self.symbol_configs = {self.choose_symbol: self.symbol_configs_data[self.choose_symbol]}

        self.symbol_num = len(self.symbol_configs.keys())
        for k, v in self.symbol_configs.items():
            s = SymbolProcess(self, v)
            self.symbol_process_map[k] = s
            self.date.update(set(s.df.index))

    def run(self):
        last_value = 0
        plt_date = []
        for date in sorted(list(self.date)):
            position_flag = 0
            for symbol, s in self.symbol_process_map.items():
                s.on_quote(date)
                if s.position and self.is_add_symbol:
                    if s.position[0] == 'long':
                        position_flag -= 1
                    if s.position[0] == 'short':
                        position_flag += 1

            if self.is_add_symbol:
                self.add_symbol.on_quote(date, position_flag)
            if not self.account_value == last_value:
                last_value = self.account_value
                plt_date.append(date)
                self.account_value_list.append(self.account_value)

        print(self.df_trade)
        print('total:', self.account_value)

        max_withdrawal = self.cal_max_withdrawal(self.account_value_list)

        for symbol, s in self.symbol_process_map.items():
            print(symbol, s.symbol_account_value)

        title = "净值记录_" + ' '.join(self.symbol_configs.keys()) + f'最大回撤：{round(max_withdrawal*100,2)}%'
        fig = make_subplots(
            rows=1, cols=1, shared_xaxes=True, print_grid=False,  # print_grid 设置为 False 以隐藏网格线
            subplot_titles=(title,)  # 修正了原来代码中的括号使用
        )

        x_min = pd.to_datetime(plt_date[0]) - pd.Timedelta(days=0.5)
        x_max = pd.to_datetime(plt_date[-1]) + pd.Timedelta(days=0.5)
        fig.update_xaxes(range=[x_min, x_max], row=1, col=1)

        fig.add_trace(go.Scatter(
            x=[pd.to_datetime(x) for x in sorted(plt_date)],
            y=self.account_value_list,
            xhoverformat="%Y-%m-%d %H:%M:%S",
            mode="lines",
            name="226净值记录"),
            row=1, col=1
        )

        # 定义特定日期
        specific_date = pd.to_datetime('2024-08-14 00:00:00')
        # 添加一个点和一条垂直线
        fig.add_shape(
            type="line",  # 线类型
            x0=specific_date, y0=min(self.account_value_list),  # 线的起点
            x1=specific_date, y1=max(self.account_value_list),  # 线的终点
            xref="x", yref="y",
            line=dict(color="red", width=1, dash="dash")  # 线的颜色、宽度和样式
        )

        specific_date = pd.to_datetime('2024-09-12 09:09:00')
        # 添加一个点和一条垂直线
        fig.add_shape(
            type="line",  # 线类型
            x0=specific_date, y0=min(self.account_value_list),  # 线的起点
            x1=specific_date, y1=max(self.account_value_list),  # 线的终点
            xref="x", yref="y",
            line=dict(color="red", width=1, dash="dash")  # 线的颜色、宽度和样式
        )

        # fig.write_html(f'./result/{title}.html')
        fig.show()

    def cal_max_withdrawal(self, account_value_list):
        max_withdrawal = 0
        for i, vlaue in enumerate(account_value_list):
            if i < 2:
                continue
            withdrawal = max(account_value_list[:i]) - vlaue
            if withdrawal > max_withdrawal:
                max_withdrawal = withdrawal
        return max_withdrawal

    def read_step_price(self):
        engine = create_engine(
            'mysql+pymysql://app:6urA&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')

        with engine.connect() as conn:
            sql = "select instrument, min_price_step from instrument_config where instrument_category = 'DIGICCY_FUTURES' and status = 'ENABLE' order by status, updated_time desc, exchange_type;"

            df = pd.read_sql(text(sql), con=conn)
            df = df.set_index('instrument')
        return df['min_price_step'].to_dict()


if __name__ == '__main__':
    a = time.time()
    # BreakOutPortfilo('EOSUSDT').run()
    BreakOutPortfilo().run()

    # symbol_list = ['EOSUSDT', 'LTCUSDT', 'AEVOUSDT', 'APEUSDT', 'BANDUSDT',
    #                'CELRUSDT', 'ONDOUSDT', 'NFPUSDT', 'PORTALUSDT', 'RLCUSDT']
    #
    # with ProcessPoolExecutor(max_workers=6) as executor:
    #     for symbol in symbol_list:
    #         executor.submit(BreakOutPortfilo(symbol).run)
    #
    # print(time.time() - a)


