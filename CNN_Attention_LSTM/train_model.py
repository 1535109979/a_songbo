import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
import models.cnn_attention_lstm as mv

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

sc = MinMaxScaler(feature_range=(0, 1))


def get_data():
    dataframe = pd.read_excel('原数据/相关性分析用表.xlsx', 'Sheet1')
    # print(dataframe)

    train_x = dataframe.iloc[375:1876, 1:7].values
    train_y = dataframe.iloc[375:1876, 1:2].values
    test_x = dataframe.iloc[1:375, 1:7].values
    test_y = dataframe.iloc[1:375, 1:2].values

    train_x = np.nan_to_num(train_x, nan=2923)
    train_y = np.nan_to_num(train_y, nan=2844)
    test_x = np.nan_to_num(test_x, nan=2923)
    test_y = np.nan_to_num(test_y, nan=2844)

    print(train_x.shape)

    x = sc.fit_transform(train_x)
    y = sc.fit_transform(train_y)
    x_ = sc.fit_transform(test_x)
    y_ = sc.fit_transform(test_y)

    x_train = []
    y_train = []

    x_test = []
    y_test = []

    for i in range(60, len(x)):
        x_train.append(x[i - 60:i, :])
        y_train.append(y[i, :])

    np.random.seed(7)
    np.random.shuffle(x_train)
    np.random.seed(7)
    np.random.shuffle(y_train)
    tf.random.set_seed(7)
    # 将训练集由list格式变为array格式
    x_train, y_train = np.array(x_train), np.array(y_train)
    y_train = np.reshape(y_train,(y_train.shape[0],))

    print(x_train.shape, y_train.shape)

    for i in range(60, len(x_)):
        x_test.append(x_[i - 60:i, :])
        y_test.append(y_[i, :])

    x_test, y_test = np.array(x_test), np.array(y_test)
    y_test = np.reshape(y_test, (y_test.shape[0],))
    print(x_test.shape, y_test.shape)

    return x_train, y_train, x_test, y_test


def train_model(x_train, y_train, x_test, y_test):
    # model = mv.conv_lstm(60,6,128)
    model = mv.lstm_model(60,6,128)

    model.compile(loss=tf.keras.losses.MeanSquaredError(),
                  optimizer=tf.keras.optimizers.Adam(1e-4))

    histroy = model.fit(x_train, y_train,
                        validation_data=(x_test, y_test),
                        epochs=200,batch_size=128,
                        callbacks=[tf.keras.callbacks.ModelCheckpoint(
                            filepath='./checkpoint_/model_lstm_model.ckpt',
                            save_weights_only=True,
                            save_best_only=True,
                            verbose=1)])


def predict(x_test, y_test):
    model = mv.lstm_model(60, 6, 128)

    model.load_weights('./checkpoint_/model_lstm_model.ckpt')

    pre = model.predict(x_test[:10])
    pre = tf.reshape(pre, (-1, 1))
    print(pre.shape)
    quit()
    pre = sc.inverse_transform(pre)
    y_test = tf.reshape(y_test, (-1, 1))
    true = sc.inverse_transform(y_test)
    plt.plot(pre[:100])
    plt.plot(true[:100])
    plt.show()


if __name__ == '__main__':
    x_train, y_train, x_test, y_test = get_data()

    # train_model(x_train, y_train, x_test[:-100], y_test[:-100])
    predict(x_test, y_test)
