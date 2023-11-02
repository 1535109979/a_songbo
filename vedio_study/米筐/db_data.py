import re
import sqlite3

import pandas as pd
import rqdatac
from sqlalchemy import create_engine, text

rqdatac.init(username='15605173271', password='songbo1997')
conn = create_engine('mysql+pymysql://app:6uRa&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')

sql = (f'select trading_date, instrument, instrument_type, exchange_type  from daily_instrument '
       f'where dominant_flag = "1" and trading_date > "2023-06-30"')
with conn.connect() as conn:
    data = pd.read_sql(text(sql), conn)

data = data[data['exchange_type'] == 'SHFE'].reset_index(drop=True)


def save_to_sqlite(table_name, df):
    with sqlite3.connect('data/future_data_tick.db') as conn:
        df.to_sql(table_name, conn, if_exists='append', index=False)


def get_data(symbol, start_date, end_date, frequency='tick'):
    variety = re.match(r'[A-Z]+', symbol).group()

    data = rqdatac.get_price(symbol,
                             start_date=start_date,
                             end_date=end_date,
                             frequency=frequency,
                             )
    data = data.reset_index()
    # print(data)
    save_to_sqlite(variety, data)


def process_variety(df):
    vari = list(set(df['instrument_type'].tolist()))[0]
    if vari in ['ag']:
        return
    print(vari)

    def process_instrument(df_instrument):
        df_instrument = df_instrument.sort_values(by='trading_date').reset_index(drop=True)

        symbol = df_instrument.loc[0].instrument.upper()
        start_date = df_instrument.loc[0].trading_date
        end_date = df_instrument.loc[len(df_instrument) - 1].trading_date
        print(symbol, start_date, end_date)
        get_data(symbol, start_date, end_date)

    df.groupby('instrument').apply(process_instrument)


data.groupby('instrument_type').apply(process_variety)
