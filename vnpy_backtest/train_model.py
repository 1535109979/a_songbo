import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.python.keras.callbacks import ModelCheckpoint
from tensorflow.python.keras.layers import *
from tensorflow.python.keras.models import Model, load_model
from tensorflow.python.keras.optimizer_v1 import Adam

from a_songbo.vnpy_backtest.data_flow import DataFlow


def lstm_model():
    v_input = Input((30, 6))
    x = LSTM(32, return_sequences=1)(v_input)
    x = LSTM(64, return_sequences=0)(x)

    x = Dense(128)(x)
    x = Dropout(rate=0.2)(x)
    x = Dense(32)(x)
    x = Dropout(rate=0.2)(x)
    out = Dense(1)(x)

    train_model = Model(v_input, out)
    train_model.compile(loss='mean_squared_error', optimizer='adam')
    train_model.summary()
    return train_model


def close_lstm_model():
    v_input = Input((10, 1))
    x = LSTM(32, return_sequences=1)(v_input)
    x = LSTM(64, return_sequences=0)(x)

    x = Dense(64)(x)
    x = Dropout(rate=0.2)(x)
    out = Dense(1)(x)

    train_model = Model(v_input, out)
    train_model.compile(loss='mean_squared_error', optimizer='Adam')
    train_model.summary()
    return train_model


def dnn_model():
    v_input = Input((30, 6))
    x = Flatten()(v_input)
    x = Dense(128)(x)
    x = Dense(256)(x)
    x = Dropout(rate=0.2)(x)
    x = Dense(512)(x)
    x = Dense(128)(x)
    x = Dropout(rate=0.2)(x)
    out = Dense(1)(x)

    train_model = Model(v_input, out)
    train_model.compile(loss='mean_squared_error', optimizer='adam')
    train_model.summary()
    return train_model


def train_model(x, y):
    name = 'test.h5'
    ckpt = ModelCheckpoint(
        filepath='result/' + name,
        monitor='loss',
        verbose=0,
        save_best_only=True,
        save_weights_only=False,
        mode='min',
        save_freq=1,
    )

    model = lstm_model()
    # model = close_lstm_model()
    # model = dnn_model()

    model.fit(x, y, batch_size=32, epochs=100,
              callbacks=[ckpt],
              validation_split=0.2,
              )


if __name__ == '__main__':
    x, y, x_, y_ = DataFlow.get_train_data()
    # x, y, x_, y_ = DataFlow.close_data()
    train_model(x, y)
