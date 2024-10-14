import logging
import multiprocessing
import os
import re
import shutil
import sys
import threading
import time
import traceback
import zipfile
from concurrent.futures import ProcessPoolExecutor

import pandas as pd
from pandas import DataFrame
from sqlalchemy import create_engine, text

from config import SaveKey,MapKey

logging.basicConfig(filename='mylogs/save_shfe_tick5', level=logging.INFO)


class SaveDominantTick():

    def __init__(self, file_queue=None,year='2020', dominant_type='88', zip_fp='/Users/edy/Downloads/SHFE/2020',
                 save_fp='/Users/edy/Downloads/dominant_files', queue_file_fp='/Users/edy/Downloads/queue_files/'):
        self.variety = None
        self.year = year
        self.dominant_type = dominant_type
        self.zip_fp = zip_fp
        self.save_fp = save_fp
        self.queue_file_fp = queue_file_fp
        self.file_queue = file_queue

        self.day_df_list = []

    def create_conn(self):
        print('create db link')
        return create_engine(
            'mysql+pymysql://app:6uRa&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/md?charset=utf8mb4')

    def get_now_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    def unzipfile(self,zip_file):
        print(f'start unzip:{self.get_now_time()}',zip_file)
        logging.info(f'{self.get_now_time()} start unzip:{zip_file}')
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(self.save_fp)

    def detele_file(self,file_fp):
        try:
            shutil.rmtree(file_fp)
            print(f'{self.get_now_time()} delete zip:{file_fp}')
            logging.info(f'delete zip:{self.get_now_time()}  {file_fp}')
        except Exception as e:
            print(f"Failed to delete {file_fp}. Reason: {e}")

    def process_data(self, df_chunk):
        try:
            day = df_chunk.loc[0].trading_day
            def cal_datetime(a, b, c):
                return pd.to_datetime(str(int(a)) + '-' + str(b) + '.' + str(c))

            df_chunk['datetime'] = df_chunk.apply(
                lambda x: cal_datetime(x['ActionDay'], x['UpdateTime'], x['UpdateMillisec']),
                axis=1)
            df_chunk['localtime'] = df_chunk['datetime'].apply(lambda x: x.timestamp() * 1000)
            df_chunk['datetime'] = df_chunk['datetime'].astype(str)
            df_chunk['id'] = df_chunk['localtime'].astype(int)
            df_chunk['instrument_category'] = 'FUTURES'
            df_chunk['exchange'] = df_chunk['exchange'].apply(lambda x: x.strip(' '))
            df_chunk['name'] = df_chunk['name'].apply(lambda x: x.strip(' '))

            df_chunk.drop_duplicates(subset='id', inplace=True)
            df_chunk = df_chunk[SaveKey]

            queue_fp = f'{self.queue_file_fp}tick5_futures_shfe_{self.variety}{self.dominant_type}__{day}.csv'
            df_chunk.to_csv(queue_fp,index=False)
            time.sleep(0.2)
            self.file_queue.put((queue_fp,f'tick5_futures_shfe_{self.variety}{self.dominant_type}'))

        except:
            traceback.print_exc()

    def split_df(self,df_csv:DataFrame):
        def append_data(df):
            self.day_df_list.append(df.reset_index(drop=True))

        df_csv.groupby('trading_day').apply(append_data)

    def start_processpool(self, df_csv):
        df_csv = df_csv.reset_index(drop=True)

        self.split_df(df_csv)

        with ProcessPoolExecutor(max_workers=10) as pool:
            pool.map(self.process_data, self.day_df_list)
            pool.shutdown(wait=True)

        self.day_df_list = []

    def read_dominant(self, ):
        with create_engine(
                'mysql+pymysql://app:6uRa&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/md?charset=utf8mb4').connect() as conn:
            sql = f'select * from dominant_futures where exchange = "SHFE" and ' \
                  f'dominant_type ="{self.dominant_type}" and date like "{self.year}%"'
            df = pd.read_sql(sql=text(sql), con=conn)
            df['fp'] = df['date'].apply(lambda x: x[:6])
            df = df.sort_values(by='date').reset_index(drop=True)

        def cal_variety(code):
            return re.match(r'[a-zA-Z]+', code).group()

        df['variety'] = df['future'].apply(cal_variety)

        def process_future(df_future: DataFrame):
            df_future = df_future.reset_index(drop=True)
            # print(df_future)
            future = df_future.loc[0].future
            month = df_future.loc[0].fp
            require_date = df_future['date'].tolist()
            self.variety = df_future.loc[0].variety

            csv_fp = f'{self.save_fp}/' + f'SHFE-{month}/{future}.csv'

            # print(f'read file:{self.get_now_time()}', csv_fp)
            logging.info(f'{self.get_now_time()} read file: {csv_fp}')

            df_csv = pd.read_csv(csv_fp, encoding='gbk')

            df_csv.columns = [MapKey[x] for x in df_csv.columns]
            df_csv = df_csv[~df_csv['ActionDay'].isnull()]
            df_csv['trading_day'] = df_csv['trading_day'].astype(str)
            df_csv = df_csv[df_csv['trading_day'].isin(require_date)]

            self.start_processpool(df_csv)
            # quit()

        def process_month(df_month: DataFrame):
            df_month = df_month.reset_index(drop=True)
            month = df_month.loc[0].fp
            logging.info(f'read file:{self.get_now_time()} {month}')

            self.unzipfile(self.zip_fp + f'{self.year}/SHFE-' + month + '.zip')
            df_month.groupby('future').apply(process_future)
            # quit()
            self.detele_file(self.save_fp + '/SHFE-' + month)




        df.groupby('fp').apply(process_month)

    def consume_queue(self):
        try:
            conn = self.create_conn()
            while True:
                if not self.file_queue.empty():
                    data = self.file_queue.get()
                    self.upload_data(data=data, conn=conn)
                else:
                    time.sleep(1)
        except Exception as e:
            traceback.print_exc()
            logging.info(f'{self.get_now_time()} consume queue fail {e}')

    def upload_data(self, data, conn):
        try:
            df = pd.read_csv(data[0])
            df.to_sql(data[1],con=conn,index=False,if_exists='append')
            os.remove(data[0])
            print(f'{self.get_now_time()} >>> upload {data[0]} to {data[1]}<<<')
            logging.info(f'{self.get_now_time()} >>> upload {data[0]} to {data[1]}<<<')
        except:
            traceback.print_exc()


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    file_queue = manager.Queue()

    s = SaveDominantTick(file_queue=file_queue)
    # s.read_dominant()
    # quit()
    p = multiprocessing.Process(target=s.read_dominant)
    p.start()

    num_threads = 10
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=s.consume_queue)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    p.join()

