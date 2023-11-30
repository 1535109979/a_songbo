import re
import sqlite3

import pandas
import pandas as pd
from sqlalchemy import create_engine, text
import rqdatac

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 500)


class BondData:
    def __init__(self):
        rqdatac.init(username='15605173271', password='songbo1997')

        df = self.read_sqlite_data()
        symbols = df['order_book_id'].tolist()
        stock_codes = df['stock_code'].tolist()

        saved_symbols = self.read_saved_symbols()

        for symbol in stock_codes:
            print(symbol)
            self.get_data(symbol)
            # quit()

    def update_data(self):
        pass

    def read_saved_symbols(self):
        symbols = []
        with sqlite3.connect('data/future_data_min.db') as connn:
            sql = f'SELECT distinct order_book_id FROM all_bond_min '
            cursor = connn.cursor()
            res = cursor.execute(sql)
            for s in res:
                symbols.append(s[0])
        return symbols

    def read_sqlite_data(self, db='data/future_data_min.db', table_name='all_bond'):
        with sqlite3.connect(db) as connn:
            sql = f'SELECT order_book_id, stock_code FROM {table_name} WHERE de_listed_date > "2023-11-14"'
            df = pd.read_sql(sql=sql, con=connn)
        return df

    def save_to_sqlite(self, df, table_name, db='data/future_data_min.db', if_exists='append'):
        with sqlite3.connect(db) as conn:
            df.to_sql(table_name, conn, if_exists=if_exists, index=False)

    def get_data(self, symbol='128075.XSHE', start_date=None, end_date=None):
        df_min: pd.DataFrame = rqdatac.get_price(symbol,
                                                 start_date=start_date,
                                                 end_date=end_date,
                                                 frequency='1m',
                                                 )
        if df_min is not None:
            print(df_min)
            df_min = df_min.reset_index()
            self.save_to_sqlite(df_min, 'all_bond_stock_min')

    def read_saved_date(self,  db='data/future_data_min.db', table_name='all_bond'):
        with sqlite3.connect(db) as connn:
            sql = f'SELECT order_book_id, stock_code FROM {table_name}'
            df = pd.read_sql(sql=sql, con=connn)


if __name__ == '__main__':
    BondData()

