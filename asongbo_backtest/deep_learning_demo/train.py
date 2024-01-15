import numpy as np
from tensorflow.python.keras.callbacks import ModelCheckpoint
from tensorflow.python.keras.layers import *
from tensorflow.python.keras.models import Model, load_model
import tensorflow as tf

from data_flow import Dataflow


def build_model():
    v_input = Input((20, 7))
    x = LSTMV1(32, activation='relu')(v_input)
    x = Dense(32, activation='relu', kernel_regularizer=tf.keras.regularizers.L1L2())(x)
    x = Dropout(0.2)(x)
    out = Dense(4, kernel_regularizer=tf.keras.regularizers.L1L2(), activation='softmax')(x)

    model = Model(v_input, out)
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model


if __name__ == '__main__':
    model = build_model()
    model.summary()
    train_x, train_y, valid_x, valid_y, test_x, test_y = Dataflow(sequence=20).get_data()
    print(train_x.shape, train_y.shape, valid_x.shape, valid_y.shape, test_x.shape, test_y.shape)

    name = 'test.h5'
    ckpt = ModelCheckpoint(
        filepath='result/' + name,
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        save_freq='epoch',
    )

    model.fit(train_x, train_y,
              epochs=100,
              batch_size=64,
              validation_data=(valid_x, valid_y),
              callbacks=[ckpt],
              )

