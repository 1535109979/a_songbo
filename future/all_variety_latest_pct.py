import sqlite3

import pandas as pd

with sqlite3.connect('./database/future_data.db') as conn:
    df = pd.read_sql('select * from future_daily_data ', conn)

data = df[['date', 'close_price', 'variety_name']]

now_vari = data[data['date'] == '2024-05-08 00:00:00']['variety_name'].to_list()
all_vari = data['variety_name'].drop_duplicates().tolist()

print(set(all_vari) - set(now_vari))

