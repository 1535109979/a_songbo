import re
import sqlite3

import pandas as pd
from sqlalchemy import create_engine, text
import rqdatac

rqdatac.init(username='15605173271', password='songbo1997')


class Rqdata_future:
    def __init__(self):
        self.saved_variety = self.read_saved_variety()
        print(len(self.saved_variety))
        self.variety = None
        self.dominant_type = '88'

    def process(self):
        self.save_future_tick_data()

    def save_future_tick_data(self):
        df = self.read_varietys()
        df = df[df['dominant_type'] == self.dominant_type]
        df = df[df['date'] > '2023-06-30 00:00:00']
        df['variety'] = df['dominant'].apply(lambda x: re.match(r'[A-Z]+', x).group())
        print(df)
        # varietys = df['variety'].unique().tolist()
        # print(varietys)

        def process_instrument(df_instrument):
            print(df_instrument)
            df_instrument = df_instrument.reset_index(drop=True)
            symbol = df_instrument.loc[0].dominant.upper()
            start_date = df_instrument.loc[0].date
            end_date = df_instrument.loc[len(df_instrument) - 1].date
            # print(symbol, start_date, end_date)
            # quit()
            self.get_data(symbol, start_date, end_date)
            print('save success')

        def process_variety(df_variety):
            self.variety = df_variety['variety'].unique().tolist()[0] + f'_{self.dominant_type}'
            if self.variety in self.saved_variety:
                return
            print(self.variety)
            df_variety.groupby('dominant').apply(process_instrument)
            quit()

        df.groupby('variety').apply(process_variety)

    def read_varietys(self):
        with sqlite3.connect('data/dominant.db') as conn:
            df = pd.read_sql(f'SELECT * FROM dominant_data', conn)
        return df

    def save_domiant_data(self):
        pass

    def read_saved_variety(self):
        with sqlite3.connect('data/future_data_tick.db') as conn:
            cursor = conn.cursor()
            result = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [x[0] for x in result]

    def save_to_sqlite(self, table_name, df):
        print(f'save to table: {table_name}')
        with sqlite3.connect('data/future_data_tick.db') as conn:
            df.to_sql(table_name, conn, if_exists='append', index=False)

    def get_data(self, symbol, start_date, end_date, frequency='tick'):
        data = rqdatac.get_price(symbol,
                                 start_date=start_date,
                                 end_date=end_date,
                                 frequency=frequency,
                                 )
        data = data.reset_index()
        # print(data)
        self.save_to_sqlite(self.variety, data)


if __name__ == '__main__':
    Rqdata_future().process()


