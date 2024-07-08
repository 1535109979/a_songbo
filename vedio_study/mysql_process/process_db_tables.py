import datetime
import re
import time

from sqlalchemy import MetaData, Table, Column, PrimaryKeyConstraint, create_engine, inspect, text,BIGINT

from config import SaveType, EXCHANGE_MAP, SaveKey
import pandas as pd


class ProcessDbTables():

    def __init__(self):
        self.conn = create_engine('mysql+pymysql://app:6uRa&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')
        # self.conn = create_engine('mysql+pymysql://root:dnNMFwYj6^8c@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4',
        #                           pool_size=6, max_overflow=10)

    def process_table(self):

        # self.alter_table_name(old_name='tick_futures_czce_cj88a2',new_name='tick_futures_czce_cj88A2')

        # self.alter_table_name(old_name='tick_futures_czce_cj88A2',new_name='tick_futures_czce_cj88a2')

        # self.check_variety_date()
        # quit()

        # self.alter_table_name('asongbo2','asongbo11')
        # quit()

        drop_list = ['ao', 'br', 'ec', 'lc', 'TS', 'TL', 'TF', 'T', 'IM', 'IH', 'IF', 'IC', 'si', 'ZC',
                               'PM', 'WH', 'RI', 'LR', 'JR', 'bb', 'RS', 'wr', 'bc', 'fb', 'CY', 'rr']
        drop_list = [x.lower() for x in drop_list]

        tabels_name = self.get_table_names()
        tabels_name = sorted(tabels_name)

        start_date = []

        for table in tabels_name:
            if table.startswith('tick_futures_'):
                variety = re.search(r'_([a-z]+)8', table).group(1)
                if variety in drop_list:
                    continue
                drop_list.append(variety)
                print(table, datetime.datetime.now())
                # sql = f'SELECT DISTINCT trading_day FROM {table} where datetime>"2020-01-01 01:16:54.000" and datetime<"2021-01-01 01:16:54.000"'
                sql = f'SELECT min(trading_day) FROM {table}'
                with self.conn.connect() as conn:
                    data = pd.read_sql(text(sql), conn)
                print((variety,data.loc[0]['min(trading_day)']))
                start_date.append((variety, data.loc[0]['min(trading_day)']))
        start_date.sort(key=lambda x: x[1])
        print(start_date)
        print(start_date[int(len(start_date)/2)])

    def check_variety_date(self):
        use_variety = [('rm', 20150105), ('cf', 20150105), ('fg', 20150105), ('ma', 20150105), ('oi', 20150105),
                       ('sf', 20150105), ('sm', 20150105), ('sr', 20150105), ('ta', 20150105), ('a', 20150105),
                       ('c', 20150105), ('cs', 20150105), ('i', 20150105), ('j', 20150105),
                       ('jd', 20150105), ('jm', 20150105), ('l', 20150105), ('m', 20150105), ('p', 20150105),
                       ('pp', 20150105), ('v', 20150105), ('y', 20150105), ('ag', 20150105), ('al', 20150105),
                       ('au', 20150105), ('bu', 20150105), ('cu', 20150105), ('hc', 20150105),
                       ('pb', 20150105), ('rb', 20150105), ('ru', 20150105), ('zn', 20150105)]
        for variety in use_variety:
            variety = variety[0]
            for variety_type in ['88', '88a2']:
                exchange = EXCHANGE_MAP[variety]
                table_name = f'tick_futures_{exchange}_{variety}{variety_type}'
                sql = f'SELECT DISTINCT trading_day FROM {table_name} where datetime>"2015-01-01 01:16:54.000" and datetime<"2016-01-01 01:16:54.000"'
                with self.conn.connect() as conn:
                    data = pd.read_sql(text(sql), conn)
                    days = data['trading_day'].tolist()
                    print(datetime.datetime.now(), table_name, len(days), days)

    def check_diff_date(self):
        tabels_name = self.get_table_names()
        tabels_name = sorted(tabels_name)

        for table in tabels_name:
            if table.startswith('tick_futures_'):
                print(table, datetime.datetime.now())

                sql = f'SELECT DISTINCT trading_day FROM {table} where datetime>"2018-01-01 01:16:54.000" and datetime<"2019-01-01 01:16:54.000"'
                with self.conn.connect() as conn:
                    data = pd.read_sql(text(sql), conn)
                    # data = conn.execute(text(sql)).fetchone()
                    days = data['trading_day'].tolist()
                    print(len(days), days)

                # self.delete_table_data(table)

        quit()

        # self.query_all_variety()
        # self.create_all_variety_table()
        # self.delete_all_table()

    def alter_tick_table_name(self):
        tables = self.get_table_names()
        for table in tables:
            if table.startswith('tick5'):
                print(table)
                cols = self.get_columns_name(table_name=table)
                col_name = [x.name for x in cols]
                for i in range(7, len(col_name)):
                    old_name = col_name[i]
                    new_name = SaveKey[i] + '_i'
                    self.alter_col_name(table_name=table, old_col_name=old_name, new_col_name=new_name)

    def query_all_variety(self):
        df = self.query_table_data(table_name='dominant_futures')
        df['variety'] = df['future'].apply(lambda x: re.match(r'[a-zA-Z]+', x).group().lower())
        df_varieties = df[['exchange', 'variety']]
        df_varieties = df_varieties.drop_duplicates().reset_index(drop=True)
        print(df_varieties)

        exchange_map = {}
        for i in range(len(df_varieties)):
            exchange = df_varieties.iloc[i]['exchange'].lower()
            variety = df_varieties.iloc[i]['variety']
            exchange_map[variety] = exchange
        print(exchange_map)

    def delete_all_table(self):
        tables = self.get_table_names()
        for table in tables:
            if table.startswith("tick_future"):
                self.delete_table(table)

    def create_all_variety_table(self):

        table_name = f'tick_futures_shfe_cwj_test'
        self.creat_table(table_name=table_name)

        # print(len(EXCHANGE_MAP))
        # for variety in EXCHANGE_MAP:
        #     exchange = EXCHANGE_MAP[variety].lower()
        #
        #     table_name = f'tick_futures_{exchange}_{variety}{88}'
        #     self.creat_table(table_name=table_name)
        #     self.creat_table(table_name=table_name+'A2')

    def query_table_data(self,table_name='',where_sql=''):
        sql = f'select * from {table_name} {where_sql}'
        with self.conn.connect() as conn:
            df = pd.read_sql(text(sql),conn)
        return df

    def alter_table_name(self,old_name='',new_name=''):
        query = f"ALTER TABLE {old_name} RENAME TO {new_name};"
        with self.conn.connect() as con:
            con.execute(text(query))
        # self.conn.connect().execute(text(query))

    def get_table_names(self):
        inspector = inspect(self.conn)
        table_names = inspector.get_table_names()
        return table_names

    def delete_table(self,table_name = 'tick_future_czce_cj88A2'):
        sql = text(f"DROP TABLE IF EXISTS {table_name};")
        print(sql)
        time.sleep(5)
        self.conn.connect().execute(sql)
        self.conn.connect().commit()

    def creat_table(self,table_name='',table_type=SaveType):
        print(f'create table {table_name}')
        metadata = MetaData()

        my_table = Table(table_name, metadata,
                         *[Column(col_name, col_type) for col_name, col_type in table_type.items()],
                         PrimaryKeyConstraint('id', name='table_name_pk')
                         )
        metadata.create_all(self.conn)

    def delete_table_data(self,table_name=''):
        sql = f'delete from {table_name} where datetime > "2023-05-01 14:59:58";'
        print(sql)
        with self.conn.connect() as con:
            con.execute(text(sql))
            con.commit()

    def get_columns_name(self,table_name = ''):
        meta = MetaData()
        table_name = table_name
        meta.reflect(bind=self.conn)
        table = meta.tables[table_name]

        return table.columns

    def alter_col_name(self,table_name='',old_col_name='',new_col_name=''):
        with self.conn.connect() as con:
            alter_query = f"alter table {table_name} change {old_col_name} {new_col_name} decimal(24, 8) null"
            con.execute(text(alter_query))


if __name__ == '__main__':
    p = ProcessDbTables()
    p.process_table()


