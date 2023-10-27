from concurrent.futures import ThreadPoolExecutor
import numpy as np


a = np.arange(106)


def load_dada(i, j):
    return a[i:j]


pool = ThreadPoolExecutor(max_workers=20)

datas = []

interval = int(len(a) / 20)
for i in range(0,len(a),interval):
    fu = pool.submit(load_dada,i,i+interval)
    datas.extend(fu.result())

print(datas)









