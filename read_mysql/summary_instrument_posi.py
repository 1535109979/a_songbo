from datetime import datetime

import pandas as pd
import pandas
from sqlalchemy import create_engine, text

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)

engine = create_engine('mysql+pymysql://app:6urA&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')
# engine = create_engine('mysql+pymysql://app:W^#&3UM4TiXL^as$@sh-cdb-0aicpi8y.sql.tencentcdb.com:60025/app?charset=utf8mb4')

with engine.connect() as conn:
    sql = ("select instrument,direction,pos_volume from user_position_info where instrument_category='FUTURES' and pos_volume != 0.0;")

    df = pd.read_sql(text(sql), con=conn)


def cal_instrument_vol(df_instrument):
    dri_vol = df_instrument.groupby('direction')['pos_volume'].sum()

    if not hasattr(dri_vol, 'SHORT'):
        return dri_vol.LONG, 0.0, dri_vol.LONG, dri_vol.LONG

    if not hasattr(dri_vol, 'LONG'):
        return 0.0, dri_vol.SHORT, -dri_vol.SHORT, dri_vol.SHORT

    return dri_vol.LONG, dri_vol.SHORT, dri_vol.LONG - dri_vol.SHORT, dri_vol.LONG + dri_vol.SHORT


df_instrument_vol = df.groupby('instrument').apply(cal_instrument_vol)
instrument_vol = pd.DataFrame(df_instrument_vol.tolist(), index=df_instrument_vol.index)
instrument_vol.columns = ['LONG', 'SHORT', 'NET', 'TOTAL']

print(instrument_vol)

# instrument_vol.to_sql('user_instrument_vol_snapshoot', engine, if_exists='append')
