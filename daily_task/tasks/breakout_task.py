import csv
import os
import sqlite3

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from sqlalchemy import create_engine, text


class BreakOutTask:

    def __init__(self):
        self.engine = create_engine(
            'mysql+pymysql://app:6urA&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')

        df = self.read_db()
        df = df.set_index('instrument')
        self.min_price_step_map = df['min_price_step'].to_dict()

        self.stop_loss_rate = 0.15
        self.commision = 0.0006
        self.trade_first = True
        self.if_trend = True
        self.start_time = '2024-01-01 00:00:00'

    def update_breakout(self):
        df_instrument_config = self.read_instrument_config()
        for i in range(len(df_instrument_config)):
            symbol = df_instrument_config.loc[i].instrument
            param_json = eval(df_instrument_config.loc[i].param_json)
            print(symbol, param_json)
            self.daily_breakout(symbol, param_json['window'], param_json['period'], param_json['rolling_window'],
                                self.start_time, float(self.min_price_step_map[symbol]))

        # self.daily_breakout('NFPUSDT', 400, 300, 200, self.start_time, float(self.min_price_step_map['NFPUSDT']))
        # self.daily_breakout('PORTALUSDT', 600, 600, 500, self.start_time, float(self.min_price_step_map['PORTALUSDT']))
        # self.daily_breakout('RLCUSDT', 400, 800, 200, self.start_time, float(self.min_price_step_map['RLCUSDT']))
        # self.daily_breakout('ONDOUSDT', 400, 700, 200, self.start_time, float(self.min_price_step_map['ONDOUSDT']))
        # self.daily_breakout('EOSUSDT', 400, 120, 200, self.start_time, float(self.min_price_step_map['EOSUSDT']))
        # self.daily_breakout('LTCUSDT', 550, 100, 550, self.start_time, float(self.min_price_step_map['LTCUSDT']))
        # self.daily_breakout('APEUSDT', 700, 600, 600, self.start_time, float(self.min_price_step_map['APEUSDT']))
        # self.daily_breakout('AEVOUSDT', 600, 320, 350, self.start_time, float(self.min_price_step_map['AEVOUSDT']))
        # self.daily_breakout('BANDUSDT', 700, 500, 700, self.start_time, float(self.min_price_step_map['BANDUSDT']))
        # self.daily_breakout('CELRUSDT', 700, 400, 600, self.start_time, float(self.min_price_step_map['CELRUSDT']))
        self.daily_breakout('MOVRUSDT', 300, 900, 300, self.start_time, float(self.min_price_step_map['MOVRUSDT']))

    def read_instrument_config(self):
        with self.engine.connect() as conn:
            sql = ("select instrument, param_json from user_instrument_config where account_id = "
                   "'binance_f_226_1234567890' and strategy_name = 'breakout' and status='ENABLE'")

            df = pd.read_sql(text(sql), con=conn)
        return df

    def read_db(self):
        with self.engine.connect() as conn:
            sql = ("select instrument, min_price_step from instrument_config where instrument_category = "
                   "'DIGICCY_FUTURES' and status = 'ENABLE' order by status, updated_time desc, exchange_type;")

            df = pd.read_sql(text(sql), con=conn)
        return df

    def daily_breakout(self, symbol, n, period, roll_mean_period, start_time, step_price):
        with sqlite3.connect('/Users/edy/byt_pub/a_songbo/binance_client/backtest/binance_quote_data.db') as conn:
            df = pd.read_sql(
                f'select * from future_{symbol} where start_time >= "{start_time}" order by start_time DESC',
                conn)

        df = df.sort_values(by='start_time').reset_index(drop=True)
        start_time = df.loc[0].start_time
        end_time = df.loc[len(df) - 1].start_time
        df['close'] = df['close'].astype(float)

        position = None
        account_value = 1
        account_value_list = []
        long_rate = []
        short_rate = []

        time_list = df['start_time'].tolist()
        close_list = df['close'].tolist()
        df['roll_mean'] = df['close'].rolling(roll_mean_period).mean()
        close_roll_mean_list = df['roll_mean'].tolist()

        df_trade = pd.DataFrame(columns=['symbol', 'time', 'offset', 'dir', 'close', 'account_value'])

        for i, close in enumerate(close_list):

            if i < n:
                continue

            time = time_list[i]
            last_n = close_list[int(i - n): i]
            last_n_max = max(last_n)
            last_n_min = min(last_n)

            # if last_n_max / last_n_min - 1 < 0.001:
            #     continue

            if position:
                flag = None
                if position[0] == 'long':
                    rate = close / position[1] - 1
                    flag = 'long'
                    if self.if_trend:
                        if close > close_roll_mean_list[i - period] > close_roll_mean_list[i - 2 * period]:
                            continue

                elif position[0] == 'short':
                    rate = 1 - close / position[1]
                    flag = 'short'

                    if self.if_trend:
                        if close < close_roll_mean_list[i - period] < close_roll_mean_list[i - 2 * period]:
                            continue

                if rate < - self.stop_loss_rate:
                    position = None
                    account_value += rate - 0.0002

                    df_trade.loc[len(df_trade)] = [symbol, time, 'stop_close', flag, close, account_value]
                    account_value_list.append(account_value)
                    continue

            if close < last_n_min:
                if not position:
                    position = ('long', close)
                    account_value += - self.commision
                    account_value_list.append(account_value)
                    df_trade.loc[len(df_trade)] = [symbol, time, 'open', 'long', close, account_value]
                else:
                    if position[0] == 'short':
                        if self.trade_first:
                            account_value += 1 - (close + step_price) / (position[1]) - self.commision
                        else:
                            account_value += 1 - close / position[1] - self.commision
                        df_trade.loc[len(df_trade)] = [symbol, time, 'close', 'short', close, account_value]

                        short_rate.append(1 - close / position[1])
                        account_value_list.append(account_value)
                        position = ('long', close)
                        df_trade.loc[len(df_trade)] = [symbol, time, 'open', 'long', close, account_value]

            elif close > last_n_max:
                if not position:
                    position = ('short', close)
                    account_value += - self.commision
                    account_value_list.append(account_value)

                    df_trade.loc[len(df_trade)] = [symbol, time, 'open', 'short', close, account_value]
                else:
                    if position[0] == 'long':
                        if self.trade_first:
                            account_value += (close - step_price) / (position[1]) - 1 - self.commision
                        else:
                            account_value += close / position[1] - 1 - self.commision
                        df_trade.loc[len(df_trade)] = [symbol, time, 'close', 'long', close, account_value]

                        long_rate.append(close / position[1] - 1)
                        account_value_list.append(account_value)

                        position = ('short', close)
                        df_trade.loc[len(df_trade)] = [symbol, time, 'open', 'short', close, account_value]

        plt.figure(figsize=(15, 6))
        plt.plot(account_value_list)
        sharpe_ratio = self.cal_sharpe(account_value_list)
        loss = self.cal_loss(account_value_list)

        print(df_trade.tail(10))

        # df_reslt.loc[len(df_reslt)] = [symbol, account_value_list[-1], sharpe_ratio, n, period, roll_mean_period]

        # save_result = True
        # if save_result:
        #     with open('result.csv', 'a', newline='') as file:
        #         writer = csv.writer(file)
        #         writer.writerow([symbol, account_value_list[-1], sharpe_ratio, n, period, roll_mean_period])

        title_name = (f'{symbol} n={n} p={period} rp={roll_mean_period} sharpe={sharpe_ratio} loss={loss} \n '
                      f' c={self.commision} sl={self.stop_loss_rate} tradetimes={len(account_value_list)}  {len(df)}min')
        plt.title(title_name)

        fp = f'result/'

        if not os.path.exists(fp):
            os.mkdir(fp)

        plt.savefig(fp + f'/{title_name}.jpg')
        plt.clf()

    def cal_sharpe(self, account_list):
        daily_returns = np.array(account_list[1:]) / np.array(account_list[:-1]) - 1
        risk_free_rate = 0.02
        annualized_return = np.mean(daily_returns) * 252
        annualized_volatility = np.std(daily_returns) * np.sqrt(252)
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
        return round(sharpe_ratio, 2)

    def cal_loss(self, account_list):
        import numpy as np
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import mean_squared_error

        model = LinearRegression()
        x_values = np.arange(len(account_list)).reshape(-1, 1)
        y_values = np.array(account_list)
        model.fit(x_values, y_values)
        y_pred = model.predict(x_values)
        loss = mean_squared_error(y_values, y_pred)
        return round(loss, 2)


if __name__ == '__main__':
    BreakOutTask().update_breakout()

