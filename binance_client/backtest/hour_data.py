import sqlite3
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas
import pandas as pd
import warnings

from sqlalchemy.dialects.mssql.information_schema import columns

warnings.filterwarnings("ignore")

pandas.set_option("expand_frame_repr", False)
# pandas.set_option("display.max_rows", 2000)


def get_all_table_name():
    with sqlite3.connect('/Users/edy/byt_pub/a_songbo/binance_client/backtest/binance_quote_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
    return tables


table_names = get_all_table_name()

symbol = 'ondousdt'
start_time = '2024-11-01 00:00:00'

df_res = pd.DataFrame(columns=['symbol','r_10','s_10', 'r_30','s_30'])

for table_name in table_names:
    table_name = table_name[0]
    symbol = table_name.split('_')[1]
    with sqlite3.connect('binance_quote_data.db') as conn:
        df = pd.read_sql(f'select start_time, open, high, low, close from {table_name} where start_time >= "{start_time}" order by start_time DESC', conn)

    df = df.sort_values(by='start_time').reset_index(drop=True)
    df['hour'] = df['start_time'].apply(lambda x: x[:-6])

    def get_hour_close(d):
        d = d.sort_values(by='start_time').reset_index(drop=True)
        open_price = d.loc[0]['open']
        high_price = d['high'].max()
        low_price = d['low'].min()
        close_price = d.loc[len(d)-1]['close']
        return float(open_price), float(high_price), float(low_price), float(close_price)

    df_hour = df.groupby('hour').apply(get_hour_close)
    df_hour = df_hour.reset_index()
    df_hour.columns =['hour', 'data']
    df_hour[['open', 'high', 'low', 'close']] = df_hour['data'].apply(pd.Series)
    df_hour['min_max_rate'] = (df_hour['high'] - df_hour['low']) / df_hour['open'] * 100
    df_hour['symbol'] = symbol
    print(df_hour[['symbol','hour','open', 'high', 'low', 'close']])
    with sqlite3.connect('binance_quote_data.db') as conn:
        df_hour[['symbol','hour','open', 'high', 'low', 'close','min_max_rate']].to_sql(name='hour_data', con=conn, if_exists='append', index=False)


    # plt.plot(df_hour['min_max_rate'])
    # plt.title('Boxplot of Data')
    # plt.show()

    # df_hour['close_normalized'] = df_hour['close'] / df_hour.loc[0]['close']
    #
    # df_hour['change_rate'] = df_hour['close'] / df_hour['close'].shift(1)
    # df_hour = df_hour.dropna()
    # df_hour = df_hour.reset_index()
    #
    # r_10 = df_hour['index'].tail(240).corr(df_hour['close'].tail(240))
    # s_10 = df_hour['close_normalized'].tail(240).std()
    # r_30 = df_hour['index'].tail(240 * 3).corr(df_hour['close'].tail(240 * 3))
    # s_30 = df_hour['close_normalized'].tail(240 * 3).std()
    #
    # df_res.loc[len(df_res)] = [symbol, abs(r_10), s_10, abs(r_30), s_30]
    # df_res = df_res.sort_values(by='r_10').reset_index(drop=True)


