import sqlite3

import akshare as ak


def save_data(df):
    with sqlite3.connect('../finance_data.db') as conn:
        df.to_sql('future_hour_data', conn, if_exists='append', index=False)



# symbol = 'IM2412'
# df = ak.futures_zh_minute_sina(symbol=symbol, period='60')

for sy in ['IF', 'IC', 'IH', 'IM']:
    symbol = sy + '2412'
    df = ak.futures_zh_minute_sina(symbol=symbol, period='60')
    df['symbol'] = symbol
    df['var'] = sy
    print(df)
    save_data(df)


