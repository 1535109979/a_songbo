import sqlite3

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.preprocessing import StandardScaler
from torch.utils.data import Dataset, DataLoader


class Dataset_Future_Tick(Dataset):
    def __init__(self):
        self.fp = '/Users/edy/byt_pub/a_songbo/vedio_study/米筐/data/future_data_tick.db'
        self.seq_len = 24
        self.data = None
        self.data_x = None
        self.data_y = None

        self.st = StandardScaler()
        self.read_tick_data()

    def read_tick_data(self):
        with sqlite3.connect(self.fp) as conn:
            df = pd.read_sql('SELECT * FROM A_88 limit 10000', conn)
        self.data = df[['last', 'a1', 'a1_v', 'b1', 'b1_v', 'change_rate']].values

        self.data = self.st.fit_transform(self.data)
        # y = torch.tensor([[0],[0],[0],[0],[0],]).expand((-1,6))
        # print('y', y.shape)
        # print(self.st.inverse_transform(y))

        self.data_x = self.data[:-1, :]
        self.data_y = np.reshape(self.data[1:, 0], (len(self.data_x), 1)).astype(np.float32)

    def __getitem__(self, index):
        print(index)
        s_begin = index
        s_end = s_begin + self.seq_len

        seq_x = self.data_x[s_begin:s_end]
        seq_y = self.data_y[s_end]

        return torch.from_numpy(seq_x), torch.from_numpy(seq_y)

    def __len__(self):
        return len(self.data_x) - self.seq_len

    def inverse_transform(self, data):
        return self.st.inverse_transform(data)


class MLPRegressor(torch.nn.Module):

    def __init__(self,):
        super(MLPRegressor, self).__init__()

        self.normlayer = torch.nn.LayerNorm(24*6)
        self.hidden = torch.nn.Linear(24*6, 64)
        self.out = torch.nn.Linear(64, 1)

    def forward(self, x):
        x = x.view(-1, 24*6).float()
        # x = torch.nn.Conv1d()
        x = self.hidden(x)
        x = F.relu(x)
        x = self.out(x)
        return x


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == '__main__':
    data_set = Dataset_Future_Tick()

    data_loader = DataLoader(
        data_set,
        batch_size=10,
        shuffle=False,
        # num_workers=5,
        drop_last=True)

    model = MLPRegressor()
    num_params = count_parameters(model)
    print('模型使用参数:{}'.format(num_params))

    optimezer = torch.optim.SGD(model.parameters(), lr=1e-3)
    criteria = torch.nn.MSELoss()

    for epoch in range(50):
        epoch_loss = []
        for i, (seq_x, seq_y) in enumerate(data_loader):
            print(seq_x.shape, seq_y.shape)
            quit()
            optimezer.zero_grad()
            pre = model(seq_x)
            loss = criteria(pre, seq_y)
            epoch_loss.append(loss.item())

            loss.backward()
            optimezer.step()
        train_loss = np.average(epoch_loss)
        print(train_loss)
