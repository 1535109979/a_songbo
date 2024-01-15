import argparse
import sqlite3

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from tensorflow.python.keras import Input, Model
from tensorflow.python.keras.layers import *
import tensorflow as tf
from PyEMD import EMD, EEMD, CEEMDAN


class EMD_lstm:
    def __init__(self, sequences=20, read_db=False, use_emd=True, plt_pre_flag=True):
        self.sequences = sequences
        self.plt_pre_flag = plt_pre_flag

        self.dataset_st = None
        self.st = StandardScaler()
        self.model = self.build_model()

        if use_emd:
            self.emd = CEEMDAN()
            self.use_emd = use_emd

        if read_db:
            self.x, self.y, self.x_, self.y_ = self.create_sequence_data()
        else:
            self.x, self.y, self.x_, self.y_ = self.read_npy()

    def train(self):
        history = self.model.fit(self.x, self.y,
                                 batch_size=32,
                                 epochs=200,
                                 validation_split=0.1,
                                 verbose=1,
                                 )
        np.save('result/lstm_imfs_loss.npy', history.history['loss'])
        np.save('result/lstm_imfs_val_loss.npy', history.history['val_loss'])

        if self.plt_pre_flag:
            self.plt_pre()

    def read_npy(self):
        x = np.load('result/x_imfs.npy')
        y = np.load('result/y.npy')
        print(x.shape)

        return x[:-50], y[:-50], x[-50:], y[-50:]

    def create_sequence_data(self):
        with sqlite3.connect('../database/future_data.db') as conn:
            df = pd.read_sql('select * from future_daily_data', conn)

        df = df[df['variety_name'] == 'PVC连续'][['date', 'close_price']]

        dataset = df["close_price"].values

        self.dataset_st = self.st.fit_transform(dataset.reshape(-1, 1))
        print(self.dataset_st.shape)

        dataX, dataY = [], []
        for i in range(len(self.dataset_st) - self.sequences - 1):
            a = self.dataset_st[i:(i + self.sequences)]
            print(i)
            if self.use_emd:
                imfs = self.emd(a.reshape(-1))
                b = np.concatenate((a, imfs.T), axis=1)
                if b.shape[1] == 4:
                    dataX.append(b)
                    dataY.append(self.dataset_st[i + self.sequences])
                    # print(dataX)
                    c = np.array(dataX)
                    print(c.shape)
            else:
                dataX.append(a)
                dataY.append(self.dataset_st[i + self.sequences])

        dataX = np.array(dataX)
        dataY = np.array(dataY)

        if self.use_emd:
            np.save('x_imfs', dataX)
            np.save('y', dataY)

        x = dataX[:-50]
        y = dataY[:-50]
        x_ = dataX[-50:]
        y_ = dataY[-50:]
        return x, y, x_, y_

    def build_model(self):
        input_shape = Input(shape=(20, 4))
        lstm1 = LSTM(32, return_sequences=1)(input_shape)
        lstm2 = LSTM(64, return_sequences=0)(lstm1)

        dense1 = Dense(32, activation="relu",
                       kernel_regularizer=tf.keras.regularizers.L2())(lstm2)
        dropout = Dropout(rate=0.2)(dense1)
        ouput_shape = Dense(1, activation="linear",
                            kernel_regularizer=tf.keras.regularizers.L2())(dropout)

        lstm_model = Model(input_shape, ouput_shape)
        lstm_model.compile(loss="mean_squared_error", optimizer="Adam")
        return lstm_model

    def plt_pre(self):
        predict_testY = self.model.predict(self.x_)
        testY_predict = self.st.inverse_transform(predict_testY)
        testY_real = self.st.inverse_transform(self.y_)

        plt.figure(figsize=(12, 8))
        plt.plot(testY_predict.reshape(-1)[:100], "b", label="pre")
        plt.plot(testY_real.reshape(-1)[:100], "r", label="real")
        plt.legend()
        plt.show()


if __name__ == '__main__':
    EMD_lstm().train()
