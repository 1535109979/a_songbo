import sqlite3
import pandas as pd


count = 0
read_le = 100000

save_col = ['symbol', 'exchange', 'datetime', 'interval', 'volume', 'turnover',
            'open_interest', 'open_price', 'high_price', 'low_price', 'close_price']

while 1:

    with sqlite3.connect('/Users/edy/byt_pub/a_songbo/vedio_study/米筐/data/stock_data.db') as conn:
        df = pd.read_sql(f'SELECT * FROM stock_daily_price limit {read_le} OFFSET {count}', conn)

        if not len(df):
            break

        df['symbol'] = df['order_book_id'].apply(lambda x: x.split('.')[0])
        df['exchange'] = 'SHFE'
        df['datetime'] = df['date']
        df['turnover'] = df['total_turnover']
        df['open_price'] = df['open']
        df['high_price'] = df['high']
        df['low_price'] = df['low']
        df['close_price'] = df['close']
        df['open_interest'] = 0
        df['interval'] = 'd'

    count += read_le

    data = df[save_col]

    print(data.loc[0])

    with sqlite3.connect('/Users/edy/.vntrader/database.db') as conn:
        data.to_sql('dbbardata', conn, if_exists='append', index=False)



