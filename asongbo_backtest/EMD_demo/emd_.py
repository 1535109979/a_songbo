import sqlite3

import matplotlib.pyplot as plt
import numpy as np
from PyEMD import EMD, EEMD, CEEMDAN
import pandas as pd

with sqlite3.connect('../database/future_data.db') as conn:
    df = pd.read_sql('select * from future_daily_data', conn)

df = df[df['variety_name'] == 'PVC连续'][['date', 'close_price']]
df['return'] = df['close_price'].pct_change()
df = df.fillna(0)
print(df)

signal = df['return'].values

emd = CEEMDAN()

imfs = emd(signal)
print(imfs.shape)

# plt.plot(imfs[7, :])
# plt.show()

residue = signal - np.sum(imfs, axis=0)

plt.figure(figsize=(10, 20))
plt.subplot(len(imfs) + 2, 1, 1)

plt.plot(range(len(df)), signal, 'b')
plt.title('EMD')

for i in range(len(imfs)):
    plt.subplot(len(imfs) + 2, 1, i+2)
    plt.plot(range(len(df)), imfs[i], 'g')
    plt.title(f'IMF {i + 1}')

plt.subplot(len(imfs) + 2, 1, len(imfs) + 2)
plt.plot(range(len(df)), residue, 'r')
plt.title('residue')

plt.tight_layout()
plt.show()
