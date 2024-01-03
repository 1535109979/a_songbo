import sqlite3

import pandas as pd

from a_songbo.vnpy_backtest.utils.bar_data_gennerator import BarGen, TickData


df_min = pd.DataFrame(columns=['symbol', 'datetime', 'start_volume', 'volume',
                           'start_turnover', 'turnover', 'open_interest',
                           'open', 'high', 'low', 'close'])


def on_bar(bar):
    global df_min
    df_min = df_min._append(bar.__dict__, ignore_index=True)


fp = '/Users/edy/byt_pub/a_songbo/vedio_study/米筐/data/future_data_tick.db'
bar_gen = BarGen('m', on_bar)


for i in range(1, 150):

    date = pd.to_datetime('2023-07-03') + pd.Timedelta(days=i)
    print(date)
    with sqlite3.connect(fp) as conn:
        df = pd.read_sql(f'SELECT * FROM A_88 where trading_date = "{date}"', conn)

    if df.empty:
        continue

    for i, row in df.iterrows():
        tick = TickData(symbol=row.order_book_id, datetime=pd.to_datetime(row.datetime), turnover=row.total_turnover,
                        volume=row.volume, open_interest=row.open_interest, limit_up=row.limit_up,
                        limit_down=row.limit_down, open=row.open, high=row.high, low=row.low, last=row['last'],
                        bid_price_1=row.b1, bid_volume_1=row.b1_v, ask_price_1=row.a1, ask_volume_1=row.a1_v
                        )
        bar_gen.on_tick(tick)

    with sqlite3.connect('./data/future_min_data.db') as conn:
        df_min.to_sql('future_min_data', conn, if_exists='append', index=False)
    print('save success')
    df_min = df_min.iloc[0:0]
