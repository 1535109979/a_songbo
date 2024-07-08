import akshare as ak
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
import matplotlib as mpl
plt.rcParams['font.sans-serif'] = ['Hiragino Sans GB']  # 指定备用字体族

plt.rcParams['axes.unicode_minus'] = False   # 解决坐标轴负数的负号显示问题

import warnings
warnings.filterwarnings('ignore')

# https://mp.weixin.qq.com/s/GWtJ2744dJONxxPOACoBNQ


def get_index_daily(symbol):
    data = ak.stock_zh_index_daily(symbol=symbol)
    return data


df = get_index_daily('sh000300')
# df = get_index_daily('sz399905')
df['date'] = pd.to_datetime(df['date'])
df['code'] = '399905'
df = df.sort_values('date').set_index('date')
print(df)

beta = np.full(df.shape[0], np.nan)
r_squared = np.full(df.shape[0], np.nan)


window_N = 16
window_M = 300

for i in range(window_N-1, len(df)):
    # 获取窗口数据
    y = df['high'].iloc[i-window_N+1:i+1].values
    X = np.c_[np.ones(window_N), df['low'].iloc[i-window_N+1:i+1].values]

    # 线性回归模型
    model = LinearRegression()
    model.fit(X, y)

    # 保存斜率和R-squared
    beta[i] = model.coef_[1]
    r_squared[i] = model.score(X, y)


df['rsrs_beta'] = beta
df['r_squared'] = r_squared


rolling_mean = df['rsrs_beta'].rolling(window=window_M).mean()
rolling_std = df['rsrs_beta'].rolling(window=window_M).std()

df['rsrs_zscore'] = (df['rsrs_beta'] - rolling_mean) / rolling_std
df['rsrs_zscore_r2'] = df['rsrs_zscore'] * df['r_squared']
df['rsrs_zscore_positive'] = df['rsrs_zscore_r2'] * df['rsrs_beta']


rsrs_list = ['rsrs_zscore', 'rsrs_zscore_r2', 'rsrs_zscore_positive']
rsrs_name = ['标准分RSRS', '修正标准分RSRS', '右偏标准分RSRS']
s = 0.7  # RSRS的阈值

timing_df = pd.DataFrame()
for i in range(len(rsrs_list)):
    rsrs = rsrs_list[i]
    timing_df[f'{rsrs_name[i]}择时'] = (df[rsrs]>=s) * 1. + (df[rsrs]<=-s) * -1.
timing_df = timing_df.replace(0, np.nan)  # 先将0替换为NA
timing_df = timing_df.fillna(method='ffill')  # 使用前值填充NA
timing_df[timing_df < 0] = 0
timing_df['不择时'] = 1.

# 计算指数每日的收益率
df['returns'] = df['close'].pct_change().shift(-1).fillna(0)
# 计算择时后的每日收益率
timing_ret = timing_df.mul(df['returns'], axis=0).dropna()
# 计算择时后的累计收益率
cumul_ret = (1 + timing_ret.fillna(0)).cumprod() - 1.


cumul_ret.plot(figsize=(10, 6), title='RSRS择时')

plt.show()


