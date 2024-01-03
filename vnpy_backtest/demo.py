import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.python.keras import layers

with sqlite3.connect('./data/future_min_data.db') as conn:
    df = pd.read_sql('select * from future_min_data', conn)
    data = df.drop('id', axis=1)

# # 读取分钟级别的期货数据
# # 假设有一个名为futures_data.csv的CSV文件，包含期货的分钟级别数据
# data = pd.read_csv('futures_data.csv')

# 选择要使用的特征
features = ['volume', 'turnover', 'open', 'high', 'low', 'close']

# 计算收盘价的增长率
data['Close_Return'] = data['close'].pct_change()

# 去除第一个NaN值
data = data.dropna()

# 归一化数据
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data[features + ['Close_Return']])


def create_sequence_data(data, window_size):
    sequences, targets = [], []
    for i in range(len(data) - window_size):
        sequence = data[i:i + window_size, :-1]  # 去除最后一列Close_Return
        target = data[i + window_size, -1]  # 最后一列是Close_Return
        sequences.append(sequence)
        targets.append(target)
    return np.array(sequences), np.array(targets)


window_size = 10
X, y = create_sequence_data(data_scaled, window_size)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = keras.Sequential([
    layers.LSTM(50, activation='relu', input_shape=(window_size, len(features))),
    layers.Dense(1)
])

model.compile(optimizer='adam', loss='mse')

model.fit(X_train, y_train, epochs=200, batch_size=32, validation_split=0.2)

loss = model.evaluate(X_test, y_test)
print(f'Test Loss: {loss}')

# 使用模型进行预测
predictions = model.predict(X_test)

fill = np.zeros((len(predictions), len(features)))
# 反归一化预测值
predictions = scaler.inverse_transform(np.concatenate((fill, predictions), axis=1))[:,-1]
y = scaler.inverse_transform(np.concatenate((fill, y_test.reshape(-1, 1)), axis=1))[:,-1]

plt.plot(predictions.reshape(-1)[:200])
plt.plot(y.reshape(-1)[:200])
plt.show()

# 计算评估指标（例如，均方根误差）
rmse = np.sqrt(np.mean((y_test - predictions) ** 2))
print(f'Root Mean Squared Error (RMSE): {rmse}')
