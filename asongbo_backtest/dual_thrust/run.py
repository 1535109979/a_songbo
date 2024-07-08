import datetime
import sqlite3
from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd

# 计算前N天的最高价－收盘价的最小值和收盘价的最大值－最低价。然后取其中的较大值，乘以k值。
# 当价格超过上轨（开盘＋触发值）时买入，或者价格低于下轨（开盘－触发值）时卖空。此策略没有止损，为正反手策略。

n = 5
k1 = 0.1
k2 = 0.1

with sqlite3.connect('../database/future_data.db') as conn:
    df_daily = pd.read_sql('select * from future_daily_data where date > "2023-01-01 00:00:00" '
                           'and date < "2023-05-01 00:00:00" and variety_name="螺纹钢连续"', conn)

# print(df_daily)

position = None
account_value = 1
account_value_list = [1]

date_num = 0
forced_times = 0
win_loss = []


def cal_win_loss(win_loss_list, a, b):
    if a >= b:
        win_loss_list.append(1)
    else:
        win_loss_list.append(0)


all_date = df_daily['date'].tolist()

for date in all_date[n+1:]:
    date_num += 1
    can_open = True
    df_last5 = df_daily[df_daily['date'] < date].tail(5)

    with sqlite3.connect('../database/future_data.db') as conn:
        sql = f'select * from future_min_data where strftime("%Y-%m-%d", datetime) == "{date[:10]}"'
        df_min = pd.read_sql(sql, conn)

    if df_min.empty:
        continue
    open = df_min.loc[0]['open']

    upper = open + (df_last5['high_price'].max() - df_last5['close_price'].min()) * k1
    low = open - (df_last5['high_price'].max() - df_last5['close_price'].min()) * k2
    print(date, open, upper, low, account_value)

    for i, close in enumerate(df_min['close'].tolist()):
        # print(i)
        if close > upper:
            if not position:
                if can_open:
                    position = ('short', close)
                    print(position)
            else:
                if position[0] == 'long':
                    # 平多
                    print('-------')
                    account_value = account_value * close / position[1]
                    cal_win_loss(win_loss, close, position[1])
                    # 开空
                    position = ('short', close)
                    print(position)
        if close < low:
            if not position:
                if can_open:
                    position = ('long', close)
                    print(position)
            else:
                if position[0] == 'short':
                    # 平空
                    print('-------')
                    account_value = account_value * position[1] / close
                    cal_win_loss(win_loss, position[1], close)
                    # 开多
                    position = ('long', close)
                    print(position)

        # if len(df_min) - i < 120 and not position:
        #     can_open = False
        #
        # if i == len(df_min)-5:
        #     if position:
        #         if position[0] == 'short':
        #             account_value = account_value * position[1] / close
        #             cal_win_loss(win_loss, position[1], close)
        #             position = None
        #         elif position[0] == 'long':
        #             account_value = account_value * close / position[1]
        #             cal_win_loss(win_loss, close, position[1])
        #             position = None
        #         forced_times += 1
        #     can_open = False
    account_value_list.append(account_value)

print(account_value, 'trading days', date_num, 'trade times:', len(win_loss), 'forced rate:', forced_times / len(win_loss),
      'win rate', sum(win_loss) / len(win_loss), )

plt.plot(account_value_list)
plt.show()

