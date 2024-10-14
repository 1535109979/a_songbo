import sqlite3

import pandas as pd

with sqlite3.connect('./database/future_data.db') as conn:
    df = pd.read_sql('select * from future_daily_data ', conn)

data = df[['date', 'close_price', 'variety_name']]

n = 90


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
print(df_pct[df_pct['date'] == '2024-05-08 00:00:00'].sort_values(by='pct'))

# now_vari = data[data['date'] == '2024-05-08 00:00:00']['variety_name'].to_list()
# all_vari = data['variety_name'].drop_duplicates().tolist()
#
# print(set(all_vari) - set(now_vari))

