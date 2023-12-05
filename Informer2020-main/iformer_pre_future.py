import sqlite3

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from torch.utils.data import Dataset, DataLoader


class Dataset_Future_Tick(Dataset):
    def __init__(self):
        self.fp = '/Users/edy/byt_pub/a_songbo/vedio_study/米筐/data/future_data_tick.db'
        self.seq_len = 24 * 4 * 4
        self.label_len = 24 * 4
        self.pred_len = 24 * 4
        self.data_x = None
        self.read_tick_data()

    def read_tick_data(self):
        with sqlite3.connect(self.fp) as conn:
            df = pd.read_sql('SELECT * FROM A_88 limit 1000', conn)
        self.data_x = df[['last', 'volume', 'a1', 'a1_v', 'b1', 'b1_v', 'change_rate']].values

    def __getitem__(self, index):
        s_begin = index
        s_end = s_begin + self.seq_len
        r_begin = s_end - self.label_len
        r_end = r_begin + self.label_len + self.pred_len

        seq_x = self.data_x[s_begin:s_end]

        return seq_x

    def __len__(self):
        return len(self.data_x) - self.seq_len - self.pred_len + 1


if __name__ == '__main__':
    data_set = Dataset_Future_Tick()
    data_loader = DataLoader(
        data_set,
        batch_size=32,
        shuffle=True,
        num_workers=5,
        drop_last=True)
    for i, seq_x in enumerate(data_loader):
        print(i)

