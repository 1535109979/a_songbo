import pandahouse as ph
import pandas as pd

df = pd.read_csv('../../米筐/data/demo.csv', index_col=0)


connection = dict(
    database='md',
    host='http://127.0.0.1:8123',
    user='default',
    password='',
)

ph.to_clickhouse(df, 'a', index=False, connection=connection)



