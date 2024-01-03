import copy
import pickle
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class DataFlow:
    with sqlite3.connect('./data/future_min_data.db') as conn:
        df = pd.read_sql('select * from future_min_data', conn)
        df = df.drop('id', axis=1)
    st = StandardScaler()

    @classmethod
    def get_train_data(cls, window_size=30):
        df = copy.deepcopy(cls.df)
        df = df[['volume', 'turnover', 'open', 'high', 'low', 'close']]
        df['rate'] = (df['close'] / df['close'].shift(1) - 1) * 10000

        sequence = df[['volume', 'turnover', 'open', 'high', 'low', 'close']].values
        sequence = cls.st.fit_transform(sequence)

        target = df['rate'].values.reshape(-1, 1)

        def create_sequence_data(sequence, target, window_size):
            X, Y = [], []
            for i in range(len(sequence) - window_size):
                X.append(sequence[i:i + window_size, :])
                Y.append(target[i + window_size])
            return np.array(X), np.array(Y)

        X, Y = create_sequence_data(sequence, target, window_size)
        print(X.shape, Y.shape)

        splite_len = int(len(df) * 0.8)

        x = X[:splite_len, :]
        x_ = X[splite_len:, :]
        y = Y[:splite_len, :]
        y_ = Y[splite_len:, :]
        print(x.shape, x_.shape, y.shape, y_.shape)
        return x, y, x_, y_

    @classmethod
    def close_data(cls):
        data = cls.df['close'].values.reshape(-1, 1)
        data = cls.st.fit_transform(data)
        print(data.shape)

        with open('./data/close_data_standard_scaler.pkl', 'wb') as file:
            pickle.dump(cls.st, file)

        def create_sequence_data(data, window_size):
            X, Y = [], []
            for i in range(len(data) - window_size):
                X.append(data[i:i + window_size, :])
                Y.append(data[i + window_size])
            return np.array(X), np.array(Y)

        X, Y = create_sequence_data(data, 10)
        print(X.shape, Y.shape)
        splite_len = int(len(X) * 0.8)

        x = X[:splite_len, :]
        x_ = X[splite_len:, :]
        y = Y[:splite_len, :]
        y_ = Y[splite_len:, :]
        print(x.shape, x_.shape, y.shape, y_.shape)
        return x, y, x_, y_


if __name__ == '__main__':
    # DataFlow.get_train_data()

    DataFlow.close_data()
