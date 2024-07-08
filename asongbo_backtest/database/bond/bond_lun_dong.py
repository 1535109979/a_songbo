import sqlite3

import pandas as pd
from matplotlib import pyplot as plt

n = 10
k = 3


def read_data(table_name):
    with sqlite3.connect('../future_data.db') as conn:
        df = pd.read_sql(f'select * from {table_name} where 日期 > "2022-01-01"', conn)
    return df


df = read_data('bond_premium')


def process_code(data):
    data = data.reset_index(drop=True)
    data = data.loc[30:]
    data = data.loc[:len(data)-20]
    return data


df_res = df.groupby('code').apply(process_code)
df_res = df_res.droplevel(0)
df_res = df_res.dropna()
df_res['score'] = df_res.eval(f'收盘价 + {k} * 转股溢价率')

print(df_res)

all_date = df_res['日期'].drop_duplicates().tolist()
all_date = sorted(all_date)

position = {}
account_value = 1
account_value_list = []
commision = 0


for date in all_date:
    df_date = df_res[df_res['日期'] == date].sort_values(by='score').reset_index(drop=True)

    if not position:
        for i in range(5):
            code = df_date.loc[i].code
            price = df_date.loc[i].收盘价
            position[code] = price
    else:
        to_del = []
        for code, price in position.items():
            try:
                row_index = df_date.loc[df_date['code'] == code].index[0]
                latest_price = df_date.loc[row_index].收盘价
                if row_index > n or latest_price < 80:
                    to_del.append(code)
                    print(code, latest_price, price)
                    account_value += 0.2 * (latest_price / price - 1 - commision)
            except:
                to_del.append(code)
                df_code = df_res[df_res['code'] == code].sort_values(by='日期').reset_index(drop=True)
                last_price = df_code.loc[len(df_code) - 1].收盘价
                print(code, last_price, price)
                account_value += 0.2 * (last_price / price - 1 - commision)

        if to_del:
            account_value_list.append(account_value)

            for code in to_del:
                del position[code]

                for i in range(len(df_date)):
                    code = df_date.loc[i].code

                    if code in position.keys():
                        continue

                    latest_price = df_date.loc[i].收盘价

                    if latest_price < 80:
                        continue

                    position[code] = latest_price
                    break

    print(account_value, position)

plt.plot(account_value_list)
plt.title(f'n={n} k={k}')
plt.show()



