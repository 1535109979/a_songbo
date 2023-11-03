import sqlite3

import pandas as pd
from sqlalchemy import create_engine, text
import rqdatac

rqdatac.init(username='15605173271', password='songbo1997')

print(rqdatac.info())

conn = create_engine('mysql+pymysql://app:6uRa&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/'
                     'app?charset=utf8mb4')

sql = 'select DISTINCT instrument_type from daily_instrument'

with conn.connect() as conn:
    data = pd.read_sql(text(sql), conn)

varietys = data['instrument_type'].tolist()
varietys = sorted(varietys)
print(varietys)

for variety in varietys:
    print(variety)
    data = rqdatac.futures.get_dominant(variety.upper(),
                                        start_date='2022-01-01',
                                        end_date='2023-11-01',
                                        rule=1,    # 0 主力 不需要rank  1 次主力并且设置 rank=2
                                        rank=2
                                        )
    data = data.reset_index()
    data['dominant_type'] = '88A2'
    # print(data)
    # quit()
    with sqlite3.connect('data/dominant.db') as conn:
        data.to_sql('dominant_data', conn, if_exists='append', index=False)
    # quit()

