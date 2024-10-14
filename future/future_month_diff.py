import sqlite3

import pandas as pd

with sqlite3.connect('database/future_data.db') as conn:
    df = pd.read_sql('select * from all_future_daily_data', conn)


print(df)

all_date = df['date'].drop_duplicates().tolist()
all_date = sorted(all_date)


for date in all_date:
    df_date = df[df['date'] == date]
    if len(df_date) < 5:
        continue
    df_date = df_date.sort_values(by='code').reset_index(drop=True)
    df_date['diff'] = df_date['close'] - df_date['close'].shift(1)
    print(df_date)
    quit()

