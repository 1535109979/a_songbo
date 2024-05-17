import math
import signal
import time
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

# import torch
#
# a = np.array([[1, 2], [3, 4]])
# b = np.array([[5, 6], [7, 8]])
# print(a*b)
#
# A = torch.tensor([[1, 2], [3, 4]])
# B = torch.tensor([[5, 6], [7, 8]])
#
# print(A)
# print(B)
# print(A * B)
#
# # 使用 einsum 进行矩阵乘法
# result = torch.einsum('ij,ij->ij', A, B)
#
# print(result)


# import signal
# import time
#
# # 定义信号处理函数
# def handle_signal(signal, frame):
#     print("收到 SIGINT 信号，程序即将退出")
#     # 执行清理操作或其他必要的逻辑
#     # ...
#
#     # 退出程序
#     # exit(0)
#
# # 注册信号处理函数
# signal.signal(signal.SIGINT, handle_signal)
#
# # 模拟程序运行
# print("按下 Ctrl+C 组合键可以触发 SIGINT 信号")
# while True:
#     # 程序持续运行
#     time.sleep(1)


# from apscheduler.schedulers.blocking import BlockingScheduler
# import datetime
# from apscheduler.executors import pool
#
#
# def job():
#     print('This is a scheduled job.')
#     print('Current time:', datetime.datetime.now())
#
#
# executor = pool.ThreadPoolExecutor(max_workers=1)
# # 创建一个调度器
# scheduler = BlockingScheduler(executors={'default': executor})
#
# # 添加一个定时任务，每隔5秒钟执行一次
# scheduler.add_job(job, 'interval', seconds=1)
# scheduler.print_jobs()
# scheduler.start()
#
# print('---')
#




