import csv
import os.path
import sqlite3
import time
import traceback

import matplotlib.pyplot as plt
import numpy as np
import pandas
import pandas as pd
from sqlalchemy import create_engine, text
from concurrent.futures import ProcessPoolExecutor

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)


def cal_sharpe(account_list):
    daily_returns = np.array(account_list[1:]) / np.array(account_list[:-1]) - 1
    risk_free_rate = 0.02
    # 计算年化收益率
    annualized_return = np.mean(daily_returns) * 252
    # 计算年化标准差
    annualized_volatility = np.std(daily_returns) * np.sqrt(252)
    # 计算夏普比率
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
    # print("Annualized Return:", annualized_return)
    # print("Annualized Volatility:", annualized_volatility)
    # print("Sharpe Ratio:", sharpe_ratio)
    return round(sharpe_ratio, 2)


def plt_account(symbol, n, period, roll_mean_period ,step_price):
    stop_loss_rate = 0.1
    commision = 0.0006
    trade_first = True
    if_trend = True
    start_time = '2024-01-01 00:00:00'
    try:
        with sqlite3.connect('binance_quote_data.db') as conn:
            df = pd.read_sql(f'select * from future_{symbol} where start_time >= "{start_time}" order by start_time DESC',
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

        df_trade = pd.DataFrame(columns=['time', 'offset', 'dir', 'close', 'account_value'])

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
                    if if_trend:
                        if close > close_roll_mean_list[i - period] > close_roll_mean_list[i - 2 * period]:
                            continue

                elif position[0] == 'short':
                    rate = 1 - close / position[1]
                    flag = 'short'

                    if if_trend:
                        if close < close_roll_mean_list[i - period] < close_roll_mean_list[i - 2 * period]:
                            continue

                if rate < -stop_loss_rate:
                    position = None
                    account_value += rate - 0.0002

                    df_trade.loc[len(df_trade)] = [time, 'stop_close', flag, close, account_value]
                    account_value_list.append(account_value)
                    continue

            if close < last_n_min:
                if not position:
                    position = ('long', close)
                    account_value += -commision
                    account_value_list.append(account_value)
                    df_trade.loc[len(df_trade)] = [time, 'open', 'long', close, account_value]
                else:
                    if position[0] == 'short':
                        if trade_first:
                            account_value += 1 - (close + step_price) / (position[1]) - commision
                        else:
                            account_value += 1 - close / position[1] - commision
                        df_trade.loc[len(df_trade)] = [time, 'close', 'short', close, account_value]

                        short_rate.append(1 - close / position[1])
                        account_value_list.append(account_value)
                        position = ('long', close)
                        df_trade.loc[len(df_trade)] = [time, 'open', 'long', close, account_value]

            elif close > last_n_max:
                if not position:
                    position = ('short', close)
                    account_value += -commision
                    account_value_list.append(account_value)

                    df_trade.loc[len(df_trade)] = [time, 'open', 'short', close, account_value]
                else:
                    if position[0] == 'long':
                        if trade_first:
                            account_value += (close - step_price) / (position[1]) - 1 - commision
                        else:
                            account_value += close / position[1] - 1 - commision
                        df_trade.loc[len(df_trade)] = [time, 'close', 'long', close, account_value]

                        long_rate.append(close / position[1] - 1)
                        account_value_list.append(account_value)

                        position = ('short', close)
                        df_trade.loc[len(df_trade)] = [time, 'open', 'short', close, account_value]

        plt.plot(account_value_list)
        sharpe_ratio = cal_sharpe(account_value_list)

        # df_reslt.loc[len(df_reslt)] = [symbol, account_value_list[-1], sharpe_ratio, n, period, roll_mean_period]

        save_result = False
        if save_result:
            with open('result.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([symbol, account_value_list[-1], sharpe_ratio, n, period, roll_mean_period])

        title_name = (f'{symbol} n={n} p={period} rp={roll_mean_period} sharpe={sharpe_ratio} \n '
                      f' c={commision} sl={stop_loss_rate} tradetimes={len(account_value_list)}  {len(df)}min')
        plt.title(title_name)

        fp = f'result/{symbol}'

        if not os.path.exists(fp):
            os.mkdir(fp)

        plt.savefig(fp + f'/{title_name}.jpg')
        plt.clf()
    except:
        traceback.print_exc()


def saved_symbols():
    with sqlite3.connect('binance_quote_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [x[0].split('_')[1] for x in tables]
        return sorted(table_names)


def read_db():
    engine = create_engine(
        'mysql+pymysql://app:6urA&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')

    with engine.connect() as conn:
        sql = "select instrument, min_price_step from instrument_config where instrument_category = 'DIGICCY_FUTURES' and status = 'ENABLE' order by status, updated_time desc, exchange_type;"

        df = pd.read_sql(text(sql), con=conn)
    return df


if __name__ == '__main__':
    saved_symbol_list = saved_symbols()

    df = read_db()
    df = df.set_index('instrument')
    min_price_step_map = df['min_price_step'].to_dict()

    with ProcessPoolExecutor(max_workers=6) as executor:
        # for symbol in saved_symbol_list[200:]:
        for symbol in ['defiusdt']:
            print(symbol)
            step_price = float(min_price_step_map[symbol.upper()])
            for n in range(100, 800, 200):
                for roll_mean_period in range(100, 800, 200):
                    for period in range(100, 800, 200):
                        executor.submit(plt_account, symbol, n, period, roll_mean_period, step_price)

                    # plt_account(symbol, n, period, roll_mean_period, start_time, step_price)

