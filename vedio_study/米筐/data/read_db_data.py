import sqlite3

import pandas as pd


class ProcessSqlite():
    def __init__(self):
        self.fp = 'future_data_tick.db'

    def process(self):
        tables = self.query_tables()
        print(tables)
        print(len(tables))
        # self.save_df('demo',df)
        self.read_df('AL')

    def query_tables(self):
        with sqlite3.connect(self.fp) as conn:
            cursor = conn.cursor()
            result = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return list(result)

    def save_df(self, table_name, df):
        with sqlite3.connect(self.fp) as conn:
            df.to_sql(table_name, conn, if_exists='append', index=False)

    def read_df(self, table_name):
        with sqlite3.connect(self.fp) as conn:
            df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
            print(df)


if __name__ == '__main__':
    ProcessSqlite().process()
