# https://akshare.akfamily.xyz/data/index/index.html
import sqlite3

import akshare as ak


def get_index_daily(symbol):
    data = ak.stock_zh_index_daily(symbol=symbol)
    return data


df = get_index_daily('sz399905')
df[['code']] = '399905'

with sqlite3.connect('../future_data.db') as conn:
    df.to_sql('stock_index', con=conn, index=False, if_exists='append')



