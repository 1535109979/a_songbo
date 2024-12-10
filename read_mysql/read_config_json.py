import pandas as pd
import pandas
from sqlalchemy import create_engine, text

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)


engine = create_engine('mysql+pymysql://app:W^#&3UM4TiXL^as$@sh-cdb-0aicpi8y.sql.tencentcdb.com:60025/app?charset=utf8mb4')

with engine.connect() as conn:
    sql = ("select * from user_instrument_config where user_id='319';")

    df = pd.read_sql(text(sql), con=conn)


for row in df.itertuples():
    instrument = row.instrument
    param_json = eval(row.param_json)
    print(instrument,end=' ')
    for k,v in param_json.items():
        print(k, v,end=' ')

    print('')


