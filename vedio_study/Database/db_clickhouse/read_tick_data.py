import pandas as pd
import sqlalchemy
from sqlalchemy import text

engine = sqlalchemy.create_engine('clickhouse://clickhouse:CK=clickhouse@49.235.94.80:8123/md_ck')

df = pd.read_sql(text('SELECT * FROM tick_futures_shfe_ag88_ck limit 1000'), engine.connect())

print(df.loc[0])
