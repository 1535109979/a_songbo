import json
import time
from datetime import datetime, timedelta

import pandas
import pandas as pd
import requests
from sqlalchemy import create_engine, text
pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)


class CheckTradeDetail:
    def __init__(self):
        self.engine = create_engine(
            'mysql+pymysql://app:6urA&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')

        self.start_time = (datetime.now().date() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        df = self.read_trade_info()

        def process_instrument(df_instrument):
            print(df_instrument.tail(10))

        df.groupby('instrument').apply(process_instrument)

    def read_trade_info(self):
        with self.engine.connect() as conn:
            sql = ("select instrument,direction,offset_flag, volume, price,profits,commission,"
                   "ADDTIME(updated_time, '8:00:00') AS new_datetime,(price*volume) as turnover "
                   f"from trade_info where account_id='binance_f_226_1234567890' and updated_time>'{self.start_time}'"
                   "order by updated_time;")

            df = pd.read_sql(text(sql), con=conn)
            # df = df.sort_values(by='new_datetime', ascending=False)
        return df


if __name__ == '__main__':
    CheckTradeDetail()

