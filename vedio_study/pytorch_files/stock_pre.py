import sqlite3

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from tensorflow.python.keras import Input, Model, layers

with sqlite3.connect('../米筐/data/stock_data.db') as connn:
    df = pd.read_sql('SELECT date,close FROM stock_daily_price where order_book_id=="000001.XSHE"', connn)

dataset = df["close"].values
# print(type(dataset), dataset)

# y = [np.sin(x) for x in np.linspace(0, 10, 100)]
# dataset = np.array(y)
# print(type(dataset))

# plt.figure(figsize=(12, 8))
# x = df["date"]
# y = df["close"]
# plt.plot(y)
# plt.show()
# quit()


def data_set(dataset, lookback):    #创建时间序列数据样本
    dataX, dataY = [], []
    for i in range(len(dataset) - lookback - 1):
        a = dataset[i:(i + lookback)]
        dataX.append(a)
        dataY.append(dataset[i + lookback])
    return np.array(dataX), np.array(dataY)


st = StandardScaler()
dataset_st = st.fit_transform(dataset.reshape(-1, 1))
print(dataset_st.shape)

train_size = int(len(dataset_st)*0.7)
test_size = len(dataset_st)-train_size
train, test = dataset_st[0:train_size], dataset_st[train_size:len(dataset_st)]

print(train.shape, test.shape)   # (1166, 1) (501, 1)

lookback = 10
trainX, trainY = data_set(train, lookback)
testX, testY = data_set(test, lookback)
print('trianX:', trainX.shape, trainY.shape)  # (1155, 10, 1) (1155, 1)
print(trainX.shape, trainY.shape)    # (1155, 10, 1) (1155, 1)

input_shape = Input(shape=(trainX.shape[1], trainX.shape[2]))
lstm1 = layers.LSTM(32, return_sequences=1)(input_shape)
lstm2 = layers.LSTM(64, return_sequences=0)(lstm1)

dense1 = layers.Dense(64, activation="relu")(lstm2)
dropout = layers.Dropout(rate=0.2)(dense1)
ouput_shape = layers.Dense(1, activation="linear")(dropout)

lstm_model = Model(input_shape, ouput_shape)
lstm_model.compile(loss="mean_squared_error", optimizer="Adam", metrics=["mse"])
lstm_model.summary()

history = lstm_model.fit(trainX, trainY, batch_size=8, epochs=2, validation_split=0.1, verbose=1)

redict_trainY = lstm_model.predict(trainX)
predict_testY = lstm_model.predict(testX)
print(predict_testY.shape)

testY_real = st.inverse_transform(testY)
testY_predict = st.inverse_transform(predict_testY)
print("Y:", testY_predict.shape)
print("Y222:", testY_real.shape)

plt.figure(figsize=(12, 8))
plt.plot(testY_predict.reshape(-1), "b", label="pre")
plt.plot(testY_real.reshape(-1), "r", label="real")
plt.legend()
plt.show()

