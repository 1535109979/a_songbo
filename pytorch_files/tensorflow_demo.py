from keras import Model, backend as K
import tensorflow as tf
from tensorflow.python.keras.layers import *


def lstm_model():
    inputs = Input(shape=(60, 6))   # (60, 6)
    x = Conv1D(65, 3, strides=1, activation='relu', padding='same')(inputs)  # (60, 65)
    x = K.expand_dims(x, axis=1)
    x = K.repeat_elements(x, rep=3, axis=1)
    print(x.shape)
    x = Conv2D(50, (3, 3), 1,)(x)
    print(x.shape)

    quit()
    x = Dropout(0.5)(x)
    x = LSTM(128, return_sequences=True, activation='relu')(x)
    x = Dense(10, activation='relu')(x)
    output = Dense(1, kernel_regularizer=tf.keras.regularizers.L1L2())(x)
    model = Model(inputs=[inputs], outputs=output)
    return model


if __name__ == '__main__':
    model = lstm_model()
    model.summary()
