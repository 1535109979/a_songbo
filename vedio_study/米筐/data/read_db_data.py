import sqlite3
import time

import pandas as pd


class ProcessSqlite:
    def __init__(self):
        self.fp = 'future_data_tick.db'  # self.fp = 'dominant.db'

    def process(self):
        tables = self.query_tables()
        print(len(tables), tables)
        # print(len(tables))
        # self.save_df('demo',df)

        # self.drop_table('IH_88')

    def save_to_clickhouse(self, df):
        a = time.time()
        import pandahouse as ph

        connection = dict(database='md', host='http://127.0.0.1:8123', user='default', password='', )

        ph.to_clickhouse(df, 'a', index=False, connection=connection)
        print('clickhouse insert time:', time.time() - a)

    def drop_table(self, table_name):
        with sqlite3.connect(self.fp) as conn:
            cursor = conn.cursor()
            sql = f'DROP TABLE {table_name}'
            print(sql)
            cursor.execute(sql)
            conn.commit()

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
        return df


if __name__ == '__main__':
    ProcessSqlite().process()
