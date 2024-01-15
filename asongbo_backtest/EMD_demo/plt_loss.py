import numpy as np
from matplotlib import pyplot as plt


loss = np.load('result/lstm_loss.npy')
val_loss = np.load('result/lstm_val_loss.npy')
loss_imfs = np.load('result/lstm_imfs_loss.npy')
val_loss_imfs = np.load('result/lstm_imfs_val_loss.npy')
print(loss.shape, val_loss.shape, loss_imfs.shape, val_loss_imfs.shape)

val_loss_mean = np.mean(val_loss[:-50])
val_loss_imfs_mean = np.mean(val_loss_imfs[:-50])
print(val_loss_mean, val_loss_imfs_mean)

# plt.plot(loss, label='loss')
# plt.plot(val_loss, label='val_loss')
# plt.legend()
# plt.show()


