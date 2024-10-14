import sqlite3

import akshare as ak


def save_data(df):
    with sqlite3.connect('future_data.db') as conn:
        df.to_sql('all_future_daily_data', conn, if_exists='append', index=False)


for year in ['22', '23', '24']:
    for m in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
        symbol = "RB" + year + m
        df = ak.futures_zh_daily_sina(symbol=symbol)
        df['code'] = symbol
        print(df)
        save_data(df)


