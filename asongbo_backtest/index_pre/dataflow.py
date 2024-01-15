import sqlite3

import numpy as np
import pandas as pd


class StockIndexDataFlow:
    def __init__(self, sequences_len=20):
        self.df = self.read_db()
        self.close_min = self.df['close'].min()
        self.close_max = self.df['close'].max()
        self.df = self.df.apply(lambda x: (x - min(x)) / (max(x) - min(x)))
        self.sequences_len = sequences_len

    def create_sequences(self):
        data_x = []
        data_y = []

        for i in range(len(self.df) - self.sequences_len):
            data_x.append(self.df.iloc[i:i+self.sequences_len, 0:2])
            data_y.append(self.df.iloc[i+self.sequences_len, -1])

        x = np.array(data_x)
        y = np.array(data_y)
        return x[:-100], y[:-100], x[-100:], y[-100:]

    def read_db(self):
        with sqlite3.connect('../database/future_data.db') as conn:
            df = pd.read_sql('select * from stock_index', conn)
        df['pct_change'] = df['close'].pct_change()
        df = df.dropna()
        return df[['volume', 'close']].reset_index(drop=True)


if __name__ == '__main__':
    StockIndexDataFlow().create_sequences()
