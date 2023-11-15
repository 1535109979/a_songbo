import re
import sqlite3

import pandas as pd
from sqlalchemy import create_engine, text
import rqdatac

rqdatac.init(username='15605173271', password='songbo1997')
conn = create_engine('mysql+pymysql://app:6uRa&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/'
                     'app?charset=utf8mb4')

saved_variety = []
with sqlite3.connect('data/future_data_min.db') as connn:
    cursor = connn.cursor()
    res = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [i for i in res]
    for table in tables:
        sql = f"SELECT DISTINCT order_book_id FROM {table[0]}"
        symbols = cursor.execute(sql)
        symbols = [x[0] for x in symbols]
        saved_variety.extend(symbols)

print(len(saved_variety), saved_variety)

with conn.connect() as conn:
    sql = ('select trading_date,instrument,instrument_type from daily_instrument '
           'where trading_date>"2023-09-13"')
    data = pd.read_sql(text(sql), conn)
    print(data)


def save_to_sqlite(table_name, df):
    with sqlite3.connect('data/future_data_min.db') as conn:
        df.to_sql(table_name, conn, if_exists='append', index=False)


def get_data(symbol, start_date, end_date, frequency='1m'):
    variety = re.match(r'[a-zA-Z]+', symbol).group()

    df_min = rqdatac.get_price(symbol,
                             start_date=start_date,
                             end_date=end_date,
                             frequency=frequency,
                             )
    df_min = df_min.reset_index()
    save_to_sqlite(variety, df_min)


def check_symbol(instrument):
    variety = re.match(r'[a-zA-Z]+', instrument).group()
    num = re.search(r'[0-9]+', instrument).group()
    if len(num) == 4:
        return instrument
    if len(num) == 3:
        return variety + '2' + num


def process_instrument(df_instrument: pd.DataFrame):
    df_instrument = df_instrument.sort_values(by='trading_date').reset_index(drop=True)

    instrument = df_instrument.loc[0].instrument
    instrument = check_symbol(instrument)
    if instrument in saved_variety:
        return
    strat_date = df_instrument.loc[0].trading_date
    end_date = df_instrument.loc[len(df_instrument) - 1].trading_date
    print(instrument, strat_date, end_date)

    get_data(instrument.upper(), strat_date, end_date)
    # quit()


data.groupby('instrument').apply(process_instrument)




