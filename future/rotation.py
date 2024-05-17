import dataclasses
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

with sqlite3.connect('./database/future_data.db') as conn:
    df = pd.read_sql('select * from future_daily_data ', conn)

data = df[['date', 'close_price', 'variety_name']]

n = 60
k = 10


def process_vari(df_vari: pd.DataFrame):
    df_vari = df_vari.sort_values(by='date').reset_index(drop=True)
    roll_min = df_vari['close_price'].rolling(n).min()
    roll_max = df_vari['close_price'].rolling(n).max()
    df_vari['pct'] = (df_vari['close_price'] - roll_min) / (roll_max - roll_min)
    df_vari = df_vari.dropna()
    return df_vari


df_pct = data.groupby('variety_name').apply(process_vari)
df_pct = df_pct.drop(columns=['variety_name'])
df_pct = df_pct.reset_index()
df_pct = df_pct[df_pct['date'] > '2020-01-01 00:00:00']


all_date = df_pct['date'].drop_duplicates().tolist()
all_date = sorted(all_date)

position = {}
account_value = 1
account_value_list = []
commision = 0.0002


@dataclasses.dataclass
class position_unit:
    name: str
    price: float
    date: str


for date in all_date:
    df_date = df_pct.query('date == @date')
    df_date = df_date.sort_values(by='pct').reset_index(drop=True)

    if not position:
        for i in range(5):
            position[df_date.loc[i].variety_name] = position_unit(
                df_date.loc[i].variety_name, df_date.loc[i].close_price, date
                )

    else:
        to_del = []
        for name, p_unit in position.items():
            row_index = df_date.loc[df_date['variety_name'] == name].index[0]

            if row_index >= k:
                to_del.append(name)

                price = df_date.loc[row_index].close_price
                account_value += 0.2 * (price / p_unit.price - 1 - commision)

        if to_del:
            account_value_list.append(account_value)

            for name in to_del:
                del position[name]

                for i in range(len(df_date)):
                    variety_name = df_date.loc[i].variety_name
                    if variety_name in position.keys():
                        continue

                    position[variety_name] = position_unit(
                        variety_name, df_date.loc[i].close_price, date
                    )
                    break

plt.plot(account_value_list)
plt.title(f'n={n}')
plt.show()

