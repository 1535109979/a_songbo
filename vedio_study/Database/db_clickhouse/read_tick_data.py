import pandas as pd
import sqlalchemy
from sqlalchemy import text,inspect


engine = sqlalchemy.create_engine('clickhouse://clickhouse:CK-clickhouse@49.235.94.80:8123/md')

df = pd.read_sql(text(sql), engine.connect())

