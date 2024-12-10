import sqlite3
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas
import pandas as pd

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)


def read_db():
    import pandas as pd
    from sqlalchemy import create_engine, text

    engine = create_engine(
        'mysql+pymysql://app:6urA&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')

    with engine.connect() as conn:
        sql = "select instrument, min_price_step from instrument_config where instrument_category = 'DIGICCY_FUTURES' and status = 'ENABLE' order by status, updated_time desc, exchange_type;"

        df = pd.read_sql(text(sql), con=conn)
    return df


class Position:
    direction: str
    price: float
    time: datetime
    volume: int

    def re_set(self):
        self.direction = None
        self.price = None
        self.time = None
        self.volume = None


df = read_db()
df = df.set_index('instrument')
min_price_step_map = df['min_price_step'].to_dict()

n = 390
change_rate = 0.07
cover_rate = -0.02
cover_muti = 1
stop_profit_rate = 0.05
stop_loss_rate = -0.1
commision = 0.0006
trade_first = True

min_price_window = n

symbol = 'eosusdt'
step_price = float(min_price_step_map[symbol.upper()])
start_time = '2024-01-01 00:00:00'

with sqlite3.connect('binance_quote_data.db') as conn:
    df = pd.read_sql(f'select * from future_{symbol} where start_time >= "{start_time}" order by start_time DESC', conn)

df = df.sort_values(by='start_time').reset_index(drop=True)
start_time = df.loc[0].start_time
end_time = df.loc[len(df)-1].start_time
df['close'] = df['close'].astype(float)

position = Position()

account_value = 1
account_value_list = []
long_rate = []
short_rate = []

time_list = df['start_time'].tolist()
close_list = df['close'].tolist()


df_trade = pd.DataFrame(columns=['time', 'offset', 'dir', 'price', 'account_value', 'hold_time'])


for i, close in enumerate(close_list):
    if i < max(n, min_price_window):
        continue

    time = pd.to_datetime(time_list[i])
    last_n = close_list[int(i - n): i]
    last_n_max = max(last_n)
    last_n_min = min(last_n)

    positive_rate = close / last_n_min - 1
    negative_rate = close / last_n_max - 1

    signal_direction = None

    if positive_rate >= change_rate:
        signal_direction = 'short'

    if negative_rate >= change_rate:
        signal_direction = 'long'

    if position:
        if position[0] == 'long':
            profit_rate = close / position[1] - 1
        elif position[0] == 'short':
            profit_rate = position[1] / close - 1

        if profit_rate >= stop_profit_rate:
            signal_direction = 'close'

        # elif profit_rate <= cover_rate:

        if profit_rate <= stop_loss_rate:
            signal_direction = 'close'

    if signal_direction:
        if not position and signal_direction != 'close':
            position = (signal_direction, close, time)
            account_value += -commision
            account_value_list.append(account_value)
            if signal_direction == 'long':
                df_trade.loc[len(df_trade)] = [time, 'open', 'long', close, account_value, None]
            if signal_direction == 'short':
                df_trade.loc[len(df_trade)] = [time, 'open', 'short', close, account_value, None]

        elif position[0] == 'long' and signal_direction == 'short':
            account_value += (close - step_price) / (position[1]) - 1 - commision
            account_value_list.append(account_value)
            df_trade.loc[len(df_trade)] = [time, 'close', 'long', close, account_value, time-position[2]]

            account_value += -commision
            account_value_list.append(account_value)
            position = ('short', close, time)
            df_trade.loc[len(df_trade)] = [time, 'open', 'short', close, account_value, None]

        elif position[0] == 'short' and signal_direction == 'long':
            account_value += 1 - (close + step_price) / (position[1]) - commision
            account_value_list.append(account_value)
            df_trade.loc[len(df_trade)] = [time, 'close', 'short', close, account_value, time-position[2]]

            account_value += -commision
            account_value_list.append(account_value)
            position = ('long', close, time)
            df_trade.loc[len(df_trade)] = [time, 'open', 'long', close, account_value, None]

        elif position[0] == 'long' and signal_direction == 'close':
            account_value += (close - step_price) / (position[1]) - 1 - commision
            account_value_list.append(account_value)
            df_trade.loc[len(df_trade)] = [time, 'close', 'long', close, account_value, time-position[2]]
            position = None

        elif position[0] == 'short' and signal_direction == 'close':
            account_value += 1 - (close + step_price) / (position[1]) - commision
            account_value_list.append(account_value)
            df_trade.loc[len(df_trade)] = [time, 'close', 'short', close, account_value, time-position[2]]
            position = None

print(df_trade)
plt.plot(account_value_list)
plt.show()

