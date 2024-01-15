import matplotlib.pyplot as plt
import numpy as np
from tensorflow.python.keras.callbacks import ModelCheckpoint

from dataflow import StockIndexDataFlow
from build_model import build_lstm_model, build_my_model
from tensorflow.python.keras.models import load_model


def train():
    x, y, x_, y_ = StockIndexDataFlow().create_sequences()
    print(x.shape, y.shape, x_.shape, y_.shape)

    # model = build_lstm_model()
    model = build_my_model()

    name = 'test.h5'

    ckpt = ModelCheckpoint(
        filepath='result/' + name,
        monitor='val_loss',
        save_best_only=True,
        mode='min',
        save_freq='epoch',
    )

    history = model.fit(x, y,
                        batch_size=64,
                        epochs=100,
                        validation_split=0.2,
                        verbose=1,
                        callbacks=[ckpt],
                        )
    np.save('result/lstm_loss.npy', history.history['loss'])
    np.save('result/lstm_val_loss.npy', history.history['val_loss'])


def pre():
    sd = StockIndexDataFlow()
    x, y, x_, y_ = sd.create_sequences()
    print(x.shape, y.shape, x_.shape, y_.shape)

    def inverte_transformer(x, min, max):
        return x * (max - min) + min

    model = load_model('result/test.h5')
    y_pre = model.predict(x_)
    plt.plot(inverte_transformer(y_pre, sd.close_min, sd.close_max), label='pre')
    plt.plot(inverte_transformer(y_, sd.close_min, sd.close_max), label='true')
    plt.legend()
    plt.show()


if __name__ == '__main__':

    # train()
    pre()

