from tensorflow.python.keras import Input, Model
from tensorflow.python.keras.layers import *
import tensorflow as tf


def build_lstm_model(input_shape=(20, 2)):
    input = Input(shape=input_shape)

    x = LSTM(32)(input)
    x = Dense(64, activation="relu")(x)
    x = Dropout(rate=0.2)(x)
    ouput = Dense(1, kernel_regularizer=tf.keras.regularizers.L2())(x)

    lstm_model = Model(input, ouput)
    lstm_model.compile(loss="mean_squared_error", optimizer="Adam")
    return lstm_model


def build_my_model(input_shape=(20, 2)):
    input = Input(shape=input_shape)

    x = LSTM(32, return_sequences=True)(input)  # 20,32

    a = Permute((2, 1))(x)                            # 32, 20
    a = Dense(20, activation='softmax')(a)      # 32, 20
    a = Permute((2, 1))(a)

    x = Multiply()([x, a])
    x = LSTM(32)(x)
    x = Dense(64, activation='relu')(x)
    x = Dropout(0.4)(x)
    x = Dense(32, activation='relu')(x)
    x = Dropout(0.4)(x)
    ouput = Dense(1)(x)

    lstm_model = Model(input, ouput)
    lstm_model.compile(loss="mean_squared_error", optimizer='adam')
    return lstm_model


if __name__ == '__main__':

    build_my_model((20, 2))

