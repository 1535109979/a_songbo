import datetime
import sqlite3
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import Counter


class Mydataset(Dataset):
    def __init__(self, xx, yy, transform=None):
        self.x = xx
        self.y = yy
        self.tranform = transform

    def __getitem__(self, index):
        x1 = self.x[index]
        y1 = self.y[index]
        if self.tranform != None:
            return self.tranform(x1), y1
        return x1, y1

    def __len__(self):
        return len(self.x)


class Dataflow:

    def __init__(self, sequence=5):
        self.sequence = sequence
        self.future_daily_data = self.read_future_data()
        self.X = []
        self.Y = []
        self.create_data()

    def create_data(self):

        def append_data(df):
            df = df.reset_index(drop=True)
            df.drop(['date', 'variety_name', 'variety', 'exchange_type'], axis=1, inplace=True)
            x = df.apply(lambda x: (x - min(x)) / (max(x) - min(x))).values

            def process_row(row):
                if row['close_price'] / row['open_price'] - 1 < -0.005:
                    return 0
                elif row['close_price'] / row['open_price'] - 1 < 0:
                    return 1
                elif row['close_price'] / row['open_price'] - 1 < 0.005:
                    return 2
                else:
                    return 3
            y = df.apply(process_row, axis=1)

            for i in range(len(df)-self.sequence):
                self.X.append(x[i:i+self.sequence, :])
                self.Y.append(y[i+self.sequence])

        self.future_daily_data.groupby('variety_name').apply(append_data)

    def read_future_data(self):
        with sqlite3.connect('../database/future_data.db') as conn:
            df = pd.read_sql('select * from future_daily_data', conn)
        return df

    def get_data(self):
        # counter = Counter(self.Y)
        # print(counter)
        # quit()

        train_x = tf.convert_to_tensor(self.X[:-11000])
        train_y = tf.convert_to_tensor(self.Y[:-11000])
        valid_x = tf.convert_to_tensor(self.X[-11000:-1000])
        valid_y = tf.convert_to_tensor(self.Y[-11000:-1000])
        test_x = tf.convert_to_tensor(self.X[-1000:])
        test_y = tf.convert_to_tensor(self.Y[-1000:])
        return train_x, train_y, valid_x, valid_y, test_x, test_y


if __name__ == '__main__':
    Dataflow().get_data()