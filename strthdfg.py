import math
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
import torch


# a = torch.zeros(7, 512).float()
# a = a[:, :96]
# print(a.shape)
#
# pe = torch.zeros(5000, 512).float()
# pe.require_grad = False
# d_model = 512
#
# position = torch.arange(0, 5000).float()
# print(position.shape)
# position = position.unsqueeze(1)
# print(position.shape)
# div_term = (torch.arange(0, d_model, 2).float() * -(math.log(10000.0) / d_model)).exp()
# print(div_term.shape)
# print(torch.sin(position * div_term).shape)
# pe[:, 0::2] = torch.sin(position * div_term)
# pe[:, 1::2] = torch.cos(position * div_term)
# print(pe.shape)
# pe = pe.unsqueeze(0)
# print(pe.shape)
# print(pe[:, :96].shape)

#
# A = torch.rand(3, 4, 5)
# B = torch.rand(3, 5, 4)
#
# result = torch.matmul(A, B)  # 张量乘法
# print(result.shape)  # [3,4,4]

# print(A.masked_fill(mask==0,-1e9))
# quit()


# import numpy as np
# from sklearn.preprocessing import StandardScaler
#
# a = np.array([[1,2], [2,3], [3,4], [4,5], [5,6]])
# s = np.array([[3], [4], [5], [6], [7]])
# print(a)
# st = StandardScaler()
#
# b = st.fit_transform(a)
# print(b)
# c = st.fit_transform(s)
# print(c)
#
# print(st.inverse_transform([[0,0]]))
# print(st.inverse_transform([[0]]))
import random

import pickle

# import numpy as np
# fill = np.zeros((10, 6))
# a = np.zeros((10, 1))
# b = np.concatenate((fill,a),axis=1)
#
# print(b.shape)

# from torch.utils.data import Dataset, DataLoader
#
#
# class Dataset_Future_Tick(Dataset):
#     def __init__(self):
#         self.data = [i for i in range(100)]
#
#     def __len__(self):
#         return len(self.data)
#
#     def __getitem__(self, index):
#         # 在这里实现获取单个样本的逻辑
#         sample = self.data[index]
#         print(sample)
#         return sample
#
# # 创建数据集实例
# dataset = Dataset_Future_Tick()
#
# # 创建数据加载器
# dataloader = DataLoader(dataset, batch_size=10, shuffle=True)
#
# # 迭代数据加载器
# for batch in dataloader:
#     # 在这里进行每个批次的处理
#     print("Batch shape:", batch.shape)
#     break

# cm = 6092.057
# cmin = 1011.499

a = [[12, 23], [34, 53]]

b = np.array(a)
print(b)



