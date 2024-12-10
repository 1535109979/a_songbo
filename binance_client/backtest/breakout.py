import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas
import pandas as pd

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)



stop_loss_rate = 0.1
commision = 0.0006
trade_first = True
n = 430
roll_mean_period = 200
period = 710
decline_rate = 0.0

symbol = 'ondousdt'
start_time = '2024-01-01 00:00:00'

with sqlite3.connect('binance_quote_data.db') as conn:
    df = pd.read_sql(f'select * from future_{symbol} where start_time >= "{start_time}" order by start_time DESC', conn)

df = df.sort_values(by='start_time').reset_index(drop=True)
start_time = df.loc[0].start_time
end_time = df.loc[len(df)-1].start_time

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

df_trade = pd.DataFrame(columns=['time', 'reverse_reason', 'offset', 'dir', 'close', 'account_value'])

signal_flag = None
for i, close in enumerate(close_list):
    positive_regression = None
    negative_regression = None
    positive_trend = None
    negative_trend = None
    signal_direction = None

    if i < max(n, 2 * period):
        continue

    time = time_list[i]
    last_n = close_list[int(i - n): i]
    last_n_max = max(last_n)
    last_n_min = min(last_n)
    min_dr = close / last_n_min - 1
    max_dr = close / last_n_max - 1

    positive_regression = close < last_n_min
    negative_regression = close > last_n_max

    positive_trend = close > close_roll_mean_list[i - period] > close_roll_mean_list[i - 2 * period]
    negative_trend = close < close_roll_mean_list[i - period] < close_roll_mean_list[i - 2 * period]

    if not position:
        if positive_regression:
            signal_flag = ['long',i,1]
            signal_direction = 'long'
        elif negative_regression:
            signal_flag = ['short',i,1]
            signal_direction = 'short'
    else:
        if positive_regression and not positive_trend:
            signal_flag = ['long',i,0]
            signal_direction = 'long'
        if negative_regression and not negative_trend:
            signal_flag = ['short',i,0]
            signal_direction = 'short'

    # if signal_flag:
    #     if signal_flag[0] == 'long' and not positive_trend and i - signal_flag[1] < 600 and min_dr > - decline_rate:
    #         signal_flag = ['long', i, 1]
    #     if signal_flag[0] == 'short' and not negative_trend and i - signal_flag[1] < 600 and max_dr < decline_rate:
    #         signal_flag = ['short', i, 1]
    #
    # if not signal_flag:
    #     continue
    # elif signal_flag[2] and i - signal_flag[1] < 600:
    #     signal_direction = signal_flag[0]

    if signal_direction:
        if not position:
            position = (signal_direction, close)
            account_value += -commision
            account_value_list.append(account_value)

        elif position[0] == 'long' and signal_direction == 'short':
            # 反手
            account_value += close / (position[1]) - 1 - commision
            account_value_list.append(account_value)
            account_value += -commision
            position = ('short', close)

        elif position[0] == 'short' and signal_direction == 'long':
            # 反手
            account_value += 1 - close / (position[1]) - commision
            account_value_list.append(account_value)
            account_value += -commision
            position = ('long', close)

        elif position[0] == 'long' and signal_direction == 'close':
            # 平仓
            account_value += close / (position[1]) - 1 - commision
            account_value_list.append(account_value)
            position = None

        elif position[0] == 'short' and signal_direction == 'close':
            # 平仓
            account_value += 1 - close / (position[1]) - commision
            account_value_list.append(account_value)
            position = None

        signal_flag = None


plt.plot(account_value_list)
plt.show()

