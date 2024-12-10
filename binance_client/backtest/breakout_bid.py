import sqlite3
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas
import pandas as pd

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)


@dataclass
class Position:
    direction: str = None
    cost: float = None
    volume: float = None


n = 390
roll_mean_period = 100
period = 100
commision = 0.0006


symbol = 'eosusdt'
start_time = '2024-10-01 00:00:00'

with sqlite3.connect('binance_quote_data.db') as conn:
    df = pd.read_sql(f'select * from future_{symbol} where start_time >= "{start_time}" order by start_time DESC', conn)


df = df.sort_values(by='start_time').reset_index(drop=True)
df['close'] = df['close'].astype(float)

time_list = df['start_time'].tolist()
close_list = df['close'].tolist()
df['roll_mean'] = df['close'].rolling(roll_mean_period).mean()
close_roll_mean_list = df['roll_mean'].tolist()

position = Position()
account_value = 1
account_value_list = []

for i, close in enumerate(close_list):
    if i < max(n, 2 * period):
        continue

    last_n = close_list[int(i - n): i]
    last_n_max = max(last_n)
    last_n_min = min(last_n)
    min_dr = close / last_n_min - 1
    max_dr = close / last_n_max - 1

    positive_regression = close < last_n_min
    negative_regression = close > last_n_max

    positive_trend = close > close_list[i - period] > close_list[i - 2 * period]
    negative_trend = close < close_list[i - period] < close_list[i - 2 * period]





