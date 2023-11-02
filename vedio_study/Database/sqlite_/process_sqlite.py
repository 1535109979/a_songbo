import sqlite3

import pandas as pd


class ProcessSqlite():
    def __init__(self):
        # fp = '/Users/edy/.vntrader/database.db'
        fp = 'example.db'
        self.connection = sqlite3.connect(fp)
        self.cursor = self.connection.cursor()

    def process(self):
        self.query_tables()

    def query_tables(self):
        result = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for row in result:
            print(row)
        self.connection.close()

    def query_tables_data(self):
        data = self.cursor.execute("SELECT * FROM dbtickdata")
        # data = self.cursor.execute("SELECT * FROM stocks")

        for row in data:
            print(row)
        self.connection.close()

    def create_table(self):
        # 创建表并插入数据
        self.cursor.execute('''CREATE TABLE stocks (date text, trans text, symbol text, qty real, price real)''')
        self.cursor.execute("INSERT INTO stocks VALUES ('2020-01-05', 'BUY', 'APPL', 100, 50.5)")
        self.connection.commit()

    def save_by_data_frame(self):
        with sqlite3.connect('example.db') as conn:
            df.to_sql('people', conn, if_exists='replace')

    def read_data_frame(self):
        with sqlite3.connect('example.db') as conn:
            df = pd.read_sql_query('SELECT * FROM stocks', conn)
            print(df)


if __name__ == '__main__':
    ProcessSqlite().process()