import akshare as ak
import matplotlib.pyplot as plt
import pandas as pd

bond = 'sz123098'
stock = 'sz300723'
convert_price = 16.84

df_stock = ak.stock_zh_a_minute(symbol=stock, period='1')[['day','close']]
df_bond = ak.stock_zh_a_minute(symbol=bond, period='1')[['day','close']]
df_stock['close'] = df_stock['close'].astype(float)
df_bond['close'] = df_bond['close'].astype(float)

df = pd.merge(df_stock, df_bond, how='outer', on='day')
df = df.dropna().reset_index(drop=True)

df['premium'] = df.eval(f'(close_y * {convert_price} / 100 / close_x - 1) * 100')
df = df[df['premium'] > -5]

print(df)

# plt.plot([x for x in df['premium'].tolist() if x > -5])
# plt.show()

import matplotlib.dates as mdates

# 将时间字符串转换为datetime对象
df['day'] = pd.to_datetime(df['day'], format='%Y-%m-%d %H:%M:%S')

# 设置x轴刻度为时间格式
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))

# 画出premium的曲线
plt.plot(df['day'], df['premium'])
plt.xlabel('Time')
plt.ylabel('Premium')
plt.show()