# import math
#
# import torch
#
#
# a = torch.zeros(7, 512).float()
# a = a[:, :96]
# print(a.shape)
#
# pe = torch.zeros(5000, 512).float()
# pe.require_grad = False
# d_model = 512
#
# position = torch.arange(0, 5000).float()
# print(position.shape)
# position = position.unsqueeze(1)
# print(position.shape)
# div_term = (torch.arange(0, d_model, 2).float() * -(math.log(10000.0) / d_model)).exp()
# print(div_term.shape)
# print(torch.sin(position * div_term).shape)
# pe[:, 0::2] = torch.sin(position * div_term)
# pe[:, 1::2] = torch.cos(position * div_term)
# print(pe.shape)
# pe = pe.unsqueeze(0)
# print(pe.shape)
# print(pe[:, :96].shape)
import numpy as np
from sklearn.preprocessing import StandardScaler

a = np.array([[1,2], [2,3], [3,4], [4,5], [5,6]])
print(a)
st = StandardScaler()

b = st.fit_transform(a)
print(b)

print(st.inverse_transform([[0,0]]))
