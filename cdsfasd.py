import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 假设我们有一个包含 OHLC 数据的 DataFrame
data = pd.DataFrame({
    'open': [1.0, 1.1, 1.2, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.9],
    'high': [1.1, 1.2, 1.3, 1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 1.0],
    'low': [0.9, 1.0, 1.1, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.8],
    'close': [1.05, 1.15, 1.25, 1.35, 1.25, 1.15, 1.05, 0.95, 0.85, 0.95]
})

# 计算 ATR
def calculate_atr(data, period):
    high_low = data['high'] - data['low']
    high_close = np.abs(data['high'] - data['close'].shift())
    low_close = np.abs(data['low'] - data['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

atr_period = 10
atr = calculate_atr(data, atr_period)
nLoss = 1 * atr  # a 的值设为 1，根据 Pine Script 代码

# 计算 Heikin Ashi 蜡烛图（如果启用）
use_heikin = False  # 假设不使用 Heikin Ashi 蜡烛图
if use_heikin:
    ha_close = (data['open'] + data['high'] + data['low'] + data['close']) / 4
    ha_open = (data['open'].shift() + data['close'].shift()) / 2
    ha_open.iloc[0] = data['open'].iloc[0]
    ha_high = pd.concat([data['high'], ha_open, ha_close], axis=1).max(axis=1)
    ha_low = pd.concat([data['low'], ha_open, ha_close], axis=1).min(axis=1)
    src = ha_close
else:
    src = data['close'].copy()  # 确保 src 是 Pandas Series

# 计算追踪止损
xATRTrailingStop = pd.Series(np.zeros(len(data)), index=data.index)
xATRTrailingStop[0] = src[0] - nLoss[0] if src[0] > src.shift(1)[0] else src[0] + nLoss[0]

for i in range(1, len(data)):
    if src[i] > xATRTrailingStop[i-1] and src[i-1] > xATRTrailingStop[i-1]:
        xATRTrailingStop[i] = max(xATRTrailingStop[i-1], src[i] - nLoss[i])
    elif src[i] < xATRTrailingStop[i-1] and src[i-1] < xATRTrailingStop[i-1]:
        xATRTrailingStop[i] = min(xATRTrailingStop[i-1], src[i] + nLoss[i])
    elif src[i] > xATRTrailingStop[i-1]:
        xATRTrailingStop[i] = src[i] - nLoss[i]
    else:
        xATRTrailingStop[i] = src[i] + nLoss[i]

# 计算位置（pos）
pos = pd.Series(np.zeros(len(data)), index=data.index)
for i in range(1, len(data)):
    if src[i-1] < xATRTrailingStop[i-1] and src[i] > xATRTrailingStop[i-1]:
        pos[i] = 1
    elif src[i-1] > xATRTrailingStop[i-1] and src[i] < xATRTrailingStop[i-1]:
        pos[i] = -1
    else:
        pos[i] = pos[i-1]

# 计算 EMA
ema_period = 1
ema = src.ewm(span=ema_period, adjust=False).mean()

# 计算买入和卖出信号
above = (ema.shift() < xATRTrailingStop.shift()) & (ema > xATRTrailingStop)
below = (ema.shift() > xATRTrailingStop.shift()) & (ema < xATRTrailingStop)

buy = (src > xATRTrailingStop) & above
sell = (src < xATRTrailingStop) & below

barbuy = src > xATRTrailingStop
barsell = src < xATRTrailingStop

# 绘制图表
plt.figure(figsize=(12, 6))
plt.plot(data['close'], label='Close', color='blue')
plt.plot(xATRTrailingStop, label='ATR Trailing Stop', color='orange', linestyle='--')
plt.plot(ema, label='EMA', color='purple')

# 绘制买入和卖出信号
plt.scatter(data.index[buy], data['close'][buy], label='Buy Signal', color='green', marker='^')
plt.scatter(data.index[sell], data['close'][sell], label='Sell Signal', color='red', marker='v')

# 设置蜡烛图颜色
candle_colors = ['green' if barbuy[i] else 'red' if barsell[i] else 'blue' for i in range(len(data))]
for i in range(len(data)):
    plt.plot([i, i], [data['low'][i], data['high'][i]], color=candle_colors[i])
    plt.plot(i, data['open'][i], 's', color=candle_colors[i])
    plt.plot(i, data['close'][i], 's', color=candle_colors[i])

plt.title('UT Bot Alerts')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.show()