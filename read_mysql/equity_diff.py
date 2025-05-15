from collections import Counter

import pandas as pd
import pandas
from matplotlib import pyplot as plt
from sqlalchemy import create_engine, text

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)

engine = create_engine('mysql+pymysql://app:6urA&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')
# engine = create_engine('mysql+pymysql://app:W^#&3UM4TiXL^as$@sh-cdb-0aicpi8y.sql.tencentcdb.com:60025/app?charset=utf8mb4')

with engine.connect() as conn:
    sql = ("select * "
           "from user_account_snapshoot where account_id IN ('binance_f_226_1234567890','binance_f_1_0923070819') "
           "and updated_time > '2024-12-14 09:56:52.50' order by updated_time DESC;")

    df = pd.read_sql(text(sql), con=conn)

print(df)

df_1 = df[df['account_id'] == 'binance_f_1_0923070819']['equity'].tolist()
df_226 = df[df['account_id'] == 'binance_f_226_1234567890']['equity'].tolist()

print(len(df_1) , len(df_226))
