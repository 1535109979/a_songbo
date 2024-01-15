import numpy as np
from tensorflow.python.keras.models import load_model

from data_flow import Dataflow

train_x, train_y, valid_x, valid_y, test_x, test_y = Dataflow(sequence=20).get_data()
model = load_model('result/test.h5')

pre_y = model.predict(test_x)
print(pre_y)

predicted_labels = np.argmax(pre_y, axis=1)
print(predicted_labels)


