import pickle

import matplotlib.pyplot as plt
from tensorflow.python.keras.models import Model, load_model

from a_songbo.vnpy_backtest.data_flow import DataFlow


def load_model_predict(x_, y_):
    model = load_model('result/test.h5')

    pre = model.predict(x_)

    # with open('./data/close_data_standard_scaler.pkl', 'rb') as file:
    #     st_loaded = pickle.load(file)
    #
    # pre = st_loaded.inverse_transform(pre)
    # y_ = st_loaded.inverse_transform(y_)

    plt.plot(pre.reshape(-1)[:100])
    plt.plot(y_.reshape(-1)[:100])
    plt.show()


if __name__ == '__main__':
    x, y, x_, y_ = DataFlow.get_train_data()
    # x, y, x_, y_ = DataFlow.close_data()
    load_model_predict(x_, y_)