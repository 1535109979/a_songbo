import time

import pandas as pd
from vnpy.trader import database
from vnpy.trader.constant import Exchange
from datetime import datetime
import sqlite3


def read_sqlite_db():
    dbm = database.get_database()

    datas = dbm.load_tick_data('rb2305', Exchange.SHFE,
                               start=datetime.fromisoformat('2023-01-03'),
                               end=datetime.fromisoformat('2023-01-04'))

    datas.sort(key=lambda x: x.datetime)


def read_data():
    with sqlite3.connect(fp) as conn:
        df = pd.read_sql_query('SELECT * FROM dbtickdata', conn)
        print(df)
        print(df.columns)


def query_time_period(symbol='rb2305'):
    with sqlite3.connect(fp) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT min(datetime),max(datetime) FROM dbtickdata where symbol='{symbol}'")
        min_datetime, max_datetime = cursor.fetchone()
        print(min_datetime,max_datetime)
    return min_datetime and max_datetime


if __name__ == '__main__':
    fp = '/Users/edy/.vntrader/database.db'
    query_time_period()

