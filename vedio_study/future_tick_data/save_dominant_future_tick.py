import logging
import multiprocessing
import os
import queue
import re
import shutil
import sys
import threading
import time
import traceback
import zipfile
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import pandas as pd
import pymysql
from sqlalchemy import create_engine

from config import MapKey, SaveKey, EXCHANGE_MAP, Float_Keys

logging.basicConfig(filename='mylogs/cal_dominant.log', level=logging.INFO)


class ReadDominantFuture():
    fp = 'all_future/'
    save_fp = 'future_tick_data/'

    def __init__(self,file_queue=None):
        self.reset_df_dominant()
        self.result_fp = 'queue_files/'

        self.file_queue = file_queue
        self.saved_month = None

    def reset_df_dominant(self):
        self.df_dominant = pd.DataFrame(columns=['date', 'future', 'dominant_type','exchange'])

    def read_files(self):

        files_years = os.listdir(self.fp)
        files_years = sorted(files_years)
        files_years = ['2022']

        for year in files_years:
            if not year.startswith('.'):
                print(year)
                files_month = sorted(os.listdir(self.fp + year))

                for month in files_month:
                    if not month.startswith('.'):
                        data_name = month.split('.')[0]

                        self.unzipfile(self.fp + year + '/'+ month)
                        self.create_process_list(self.save_fp + data_name)
                        self.detele_file(self.save_fp + data_name)

                        while self.file_queue.qsize() > 100:
                            print('剩余未上传文件数量：',self.file_queue.qsize())
                            time.sleep(30)

    def create_process_list(self,data_fp):
        process_list = []
        exchanges = os.listdir(data_fp)
        exchanges = sorted(exchanges)
        for exchange in exchanges:
            if not exchange.startswith('.'):
                day_files = os.listdir(data_fp + '/' + exchange)
                day_files = sorted(day_files)

                for day_file in day_files:
                    if not day_file.startswith('.'):

                        csv_files = os.listdir(data_fp + '/' + exchange + '/' + day_file)
                        csv_files = sorted(csv_files)
                        for csv_name in csv_files:
                            if not csv_name.startswith('.'):
                                csv_fp = data_fp + '/' + exchange + '/' + day_file + '/' + csv_name

                                if re.match(r'[a-zA-Z]+主力连续_\d+.csv', csv_name):
                                    process_list.append((csv_fp,'88'))

                                # elif re.match(r'[a-zA-Z]+次主力连续_\d+.csv', csv_name):
                                #     process_list.append((csv_fp,'88A2'))

        print(len(process_list))

        with ProcessPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.process_data, data) for data in process_list]
            for future in futures:
                result = future.result()

    def process_data(self,data):
        try:
            csv_fp = data[0]
            dominant_type = data[1]
            file_name = csv_fp.split('/')[-1]
            variety = re.match('[a-zA-Z]+',file_name).group().lower()
            exchange = EXCHANGE_MAP[variety]

            df_csv = pd.read_csv(csv_fp, encoding='gbk')

            df_csv.columns = [MapKey[x] for x in df_csv.columns]
            df_csv = df_csv[~df_csv['ActionDay'].isnull()]
            df_csv['trading_day'] = df_csv['trading_day'].astype(str)
            df_csv['exchange'] = exchange
            df_csv['exchange'] = df_csv['exchange'].astype(str)

            def cal_datetime(a, b, c):
                return pd.to_datetime(str(int(a)) + '-' + str(b) + '.' + str(c))

            df_csv['datetime'] = df_csv.apply(
                lambda x: cal_datetime(x['ActionDay'], x['UpdateTime'], x['UpdateMillisec']),
                axis=1)
            df_csv['localtime'] = df_csv['datetime'].apply(lambda x: x.timestamp() * 1000)
            df_csv['datetime'] = df_csv['datetime'].astype(str)
            df_csv['id'] = df_csv['localtime'].astype(int)
            df_csv['instrument_category'] = 'FUTURES'
            df_csv['name'] = df_csv['name'].apply(lambda x: x.strip(' '))
            df_csv.drop_duplicates(subset='id', inplace=True)
            df_csv = df_csv[SaveKey]

            # print(f'{self.result_fp}{file_name.split(".")[0]}_{dominant_type}.csv')
            df_csv.to_csv(f'{self.result_fp}{file_name.split(".")[0]}_{dominant_type}.csv', header=False, index=False)
            time.sleep(0.5)
            to_process_file = f'{self.result_fp}{file_name.split(".")[0]}_{dominant_type}.csv'
            self.file_queue.put(f'{self.result_fp}{file_name.split(".")[0]}_{dominant_type}.csv')
            # print(self.file_queue.qsize())
        except Exception as e:
            traceback.print_exc()
            logging.info(f'{self.get_now_time()} fail {e}')

    def get_now_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    def detele_file(self,file_fp):
        try:
            shutil.rmtree(file_fp)
            print(f'{self.get_now_time()} delete {file_fp}')
            logging.info(f'{self.get_now_time()} delete {file_fp}')
        except Exception as e:
            print(f"Failed to delete {file_fp}  Reason: {e}")
            logging.info(f'Failed to delete {file_fp}  Reason: {e}')

    def unzipfile(self,zip_file):
        print(f'{self.get_now_time()} start unzip:',zip_file)
        logging.info(f'{self.get_now_time()} start unzip : {zip_file}')
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            for info in zip_ref.infolist():
                # 解决中文乱码问题
                info.filename = info.filename.encode('cp437').decode('gbk')
                zip_ref.extract(info, self.save_fp, pwd=None)

    def connect_db(self):
        conn = create_engine(
            'mysql+pymysql://app:6uRa&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/md?charset=utf8mb4')

        print('db link success')
        return conn

    def consume_queue(self):
        try:
            conn= self.connect_db()
            while True:
                if not self.file_queue.empty():
                    data = self.file_queue.get()
                    self.upload_data(data_fp=data,conn=conn)
                else:
                    time.sleep(1)
        except Exception as e:
            traceback.print_exc()
            logging.info(f'{self.get_now_time()} fail {e}')

    def upload_data(self,data_fp='',conn=None):
        try:
            df = pd.read_csv(data_fp,header=None)
            df.columns = SaveKey
            df['localtime'] = df['localtime'].astype(float)
            for col in Float_Keys:
                df[col] = df[col].astype(float)

            file_name = data_fp.split('/')[-1]
            name = file_name.split('.')[0]
            variety = re.match(r'[a-zA-Z]+',name).group().lower()
            exchange = EXCHANGE_MAP[variety]
            dominant_type = name.split('_')[-1]
            print(f'{self.get_now_time()} upload {data_fp} to tick_future_{exchange}_{variety}{dominant_type}')

            df.to_sql(name=f'tick_futures_{exchange}_{variety}{dominant_type}',con=conn,index=False,if_exists='append')
            logging.info(f'{self.get_now_time()} upload {data_fp} to tick_future_{exchange}_{variety}{dominant_type}')
            os.remove(data_fp)
        except:
            with open('result/error','a') as f:
                f.write(f'{data_fp}\n')
            self.file_queue.put(data_fp)
            traceback.print_exc()


def process_release_files(file_queue):
    fp = 'queue_files/'
    files = sorted(os.listdir(fp))
    for file in files:
        if not file.startswith('.'):
            file_queue.put(fp + file)


def process_and_upload_data(r):
    p = multiprocessing.Process(target=r.read_files)
    p.start()

    num_threads = 15
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=r.consume_queue)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    p.join()


def process_data(r):
    r.read_files()


def upload_data(r):
    process_release_files(file_queue=r.file_queue)
    print(r.file_queue.qsize())

    num_threads = 15
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=r.consume_queue)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    file_queue = manager.Queue()

    r = ReadDominantFuture(file_queue=file_queue)

    if sys.argv[1] == 'p':
        process_data(r)
    elif sys.argv[1] == 'u':
        upload_data(r)
    elif sys.argv[1] == 'pu':
        process_and_upload_data(r)
