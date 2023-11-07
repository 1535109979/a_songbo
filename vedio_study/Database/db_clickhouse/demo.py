import time

import pandahouse as ph
import pandas as pd
from clickhouse_driver import Client
from sqlalchemy import create_engine, text


# client = Client(host='localhost', port=9000)
#
# t = time.time()
#
# result = client.execute('SELECT * FROM md.a')
# print(result)
# print(len(result), time.time() - t)
# quit()


t = time.time()

conn = create_engine('mysql+pymysql://app:6uRa&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/'
                     'md?charset=utf8mb4')

sql = 'select * from tick5_futures_shfe_ag88'

with conn.connect() as conn:
    data = pd.read_sql(text(sql), conn)
    print(len(data), time.time() - t)


"""
sd


CREATE TABLE md.a
(   
    order_book_id String,
    datetime String,
    trading_date String,
    open Float32,
    last Float32,
    high Float32,
    low Float32,
    prev_settlement Float32,
    prev_close Float32,
    volume Float32,
    open_interest Float32,
    total_turnover Float32,
    limit_up Float32,
    limit_down Float32,
    a1 Float32,
    a2 Float32,
    a3 Float32,
    a4 Float32,
    a5 Float32,
    b1 Float32,
    b2 Float32,
    b3 Float32,
    b4 Float32,
    b5 Float32,
    a1_v Float32,
    a2_v Float32,
    a3_v Float32,
    a4_v Float32,
    a5_v Float32,
    b1_v Float32,
    b2_v Float32,
    b3_v Float32,
    b4_v Float32,
    b5_v Float32,
    change_rate Float32,
)
ENGINE = MergeTree()
PRIMARY KEY (order_book_id, datetime)




ALTER TABLE md.a DELETE WHERE

SELECT COUNT(*) FROM md.a;

"""
