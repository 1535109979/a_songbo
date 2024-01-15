import datetime
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd


with sqlite3.connect('../database/future_data.db') as conn:
    df = pd.read_sql('select * from future_daily_data', conn)

df = df.sort_values(by='date')

periods = 120
df['return'] = df.groupby('variety')['close_price'].pct_change(periods=periods)
df['interest_22mean'] = df.groupby('variety')['open_interest'].transform(lambda x: x.rolling(22).mean())
df = df[df['date'] > '2015-01-01']
df['date'] = pd.to_datetime(df['date'])
df['next_22_price'] = df['close_price'].shift(-22)
df = df.dropna()


def get_data(df_date):
    df_date = df_date[df_date['interest_22mean'] > 100000]
    return df_date.nlargest(5, 'return')
    # return df_date.nsmallest(5, 'return')


top_returns = df.groupby('date').apply(get_data).reset_index(drop=True).sort_values(by='date')

# print(top_returns.head(20))
# print(top_returns.loc[0])


all_date = list(set(top_returns['date'].tolist()))
all_date.sort()

interval = 22
index = interval
change_position_date = all_date[index]
print(change_position_date)

position = None
account_value = 1
account_value_list = [1]

for date in all_date[:-interval]:
    df_date = top_returns[top_returns['date'] == date][['date', 'close_price', 'variety_name']]
    varietys = df_date.set_index('variety_name')['close_price'].to_dict()

    if not position:
        position = varietys
        print(date, 'position', position)
    else:
        if date == change_position_date:
            print('--------', date, '进入换仓日,净值', account_value, '--------')
            if len(df_date) < 5:
                index += 1
                change_position_date = all_date[index]
                continue

            index += interval
            change_position_date = all_date[index]
            # print(change_position_date)

            new_account_value = 0

            position_copy = position.copy()
            for k, v in position_copy.items():
                if k not in varietys:
                    print(k, date)
                    result = df.query('date<=@date and variety_name==@k')['close_price'].values[-1]
                    new_account_value += account_value * 0.2 * (v / result) * (1 - 0.001)
                    # new_account_value += account_value * 0.2 * (result / v) * (1 - 0.001)
                    print('del:', k, v, result, v / result)
                    position.pop(k)
                else:
                    new_account_value += account_value * 0.2
            account_value = new_account_value
            account_value_list.append(account_value)

            for k, v in varietys.items():
                if k not in position:
                    print('add:', k)
                    position[k] = v
            print(date, 'position', position)
            print(date, '净值', account_value)

plt.plot(account_value_list)
plt.title(f'change position interval={interval} trading day, pct_change period={periods}')
plt.savefig('./result/demo.png')

plt.show()
