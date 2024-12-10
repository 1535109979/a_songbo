import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

with sqlite3.connect('../finance_data.db') as conn:
    df = pd.read_sql('SELECT * FROM future_hour_data', conn)

df_im = df.query('symbol == "IM2412"').sort_values(by='datetime').reset_index(drop=True)
df_im['change'] = df_im['close'] / df_im['close'].shift(1)
df_ic = df.query('symbol == "IC2412"').sort_values(by='datetime').reset_index(drop=True)
df_ic['change'] = df_ic['close'] / df_ic['close'].shift(1)
df_if = df.query('symbol == "IF2412"').sort_values(by='datetime').reset_index(drop=True)
df_if['change'] = df_if['close'] / df_if['close'].shift(1)
df_ih = df.query('symbol == "IH2412"').sort_values(by='datetime').reset_index(drop=True)
df_ih['change'] = df_ih['close'] / df_ih['close'].shift(1)

df_all = pd.DataFrame()

col = 'change'

df_all['im'] = df_im[col]
df_all['ic'] = df_ic[col]
df_all['if'] = df_if[col]
df_all['ih'] = df_ih[col]

print(df_all.head())

plt.figure(figsize=(25, 6))
plt.plot(df_all['im'] - df_all['ih'])
# plt.plot(df_all['ic'] - df_all['ih'])
# plt.plot(df_all['if'] - df_all['ih'])
plt.show()

