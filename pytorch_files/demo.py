import torch
from torch import nn


class ModelDemo(nn.Module):
    def __init__(self):
        super().__init__()
        self.l = nn.Linear(10, 8)
        self.conv = nn.Conv2d(3, 12, 3)
        self.ls = nn.LSTM(48, 5, batch_first=True)

    def forward(self, x):
        print(x.shape)
        x = self.l(x)
        print(x.shape)
        x = self.conv(x)
        x = x.view(10, 12, -1)
        print(x.shape)
        x, _ = self.ls(x)
        print(x.shape)


net = ModelDemo()

x = torch.randn((10, 3, 10, 10))

net(x)
