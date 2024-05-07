import sqlite3
from datetime import datetime

import akshare as ak
import pandas as pd

with sqlite3.connect('../future_data.db') as conn:
    df_all_stock = pd.read_sql('select * from all_stock where market_value > 10000000000 '
                               'and market_value < 50000000000', conn)


for i in range(len(df_all_stock)):
    code = df_all_stock.loc[i].code
    exchange = df_all_stock.loc[i].exchange
    print(i, code)

    data = ak.stock_zh_a_hist(symbol=code, start_date="20220101", end_date=datetime.now().strftime('%Y%m%d'))
    data['code'] = code
    data['exchange'] = exchange

    with sqlite3.connect('../future_data.db') as conn:
        data.to_sql('stock_daily_data', con=conn, index=False, if_exists='append')



