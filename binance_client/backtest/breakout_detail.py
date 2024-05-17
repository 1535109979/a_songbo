import sqlite3

import matplotlib.pyplot as plt
import pandas
import pandas as pd

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)

# 当前价格 低于 前n小时最小值，做多
# 当前价格 高于 前n小时最大值，做空
n = 10
stop_loss_rate = 0.05
commision = 0.00035
symbol = 'eosusdt'
start_time = '2024-01-16 16:44:00'

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
        elif position[0] == 'short':
            rate = 1 - close / position[1]
            flag = 'short'

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
                account_value += close / position[1] - 1 - commision
                df_trade.loc[len(df_trade)] = [time, 'close', 'long', close, account_value]

                long_rate.append(close / position[1] - 1)
                account_value_list.append(account_value)

                position = ('short', close)
                df_trade.loc[len(df_trade)] = [time, 'open', 'short', close, account_value]

print(df_trade)
# df_trade.to_csv('trade.csv')

# plt.scatter(range(len(short_rate)), short_rate)
# plt.show()
#
# plt.subplot(2,1,1)
# plt.plot(df['close'])
# plt.subplot(2,1,2)
plt.plot(account_value_list)

plt.title(f'{start_time}-->{end_time}    {len(df)}min\n '
          f'{symbol}  n={n}   trade times={len(account_value_list)} c={commision} sl={stop_loss_rate}')
plt.show()

