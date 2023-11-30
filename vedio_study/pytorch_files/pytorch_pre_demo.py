import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.nn.functional as F


device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

x = torch.unsqueeze(torch.linspace(-1, 1, 100), dim=1)
y = x.pow(2) + 0.2 * torch.rand(x.size())

# print(x)
# print(y.size())

# plt.scatter(x.data.numpy(), y.data.numpy())
# plt.show()


class MLPRegressor(torch.nn.Module):

    def __init__(self, n_feature, n_hidden, n_output):
        super(MLPRegressor, self).__init__()

        self.hidden = torch.nn.Linear(n_feature, n_hidden)

        self.out = torch.nn.Linear(n_hidden, n_output)
        print(self.modules())

    def forward(self, x):
        x = self.hidden(x)
        x = F.relu(x)
        x = self.out(x)
        return x


net = MLPRegressor(n_feature=1, n_hidden=10, n_output=1)
quit()

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


num_params = count_parameters(net)
print('使用参数:{}'.format(num_params))
# print(net)

optimezer = torch.optim.SGD(net.parameters(), lr=0.2)
criteria = torch.nn.MSELoss()

plt.ion()  # 开启交互模式

for t in range(200):
    optimezer.zero_grad()

    prediction = net(x)

    loss = criteria(prediction, y)

    loss.backward()
    optimezer.step()

    # if t % 5 == 0:
    #     plt.cla()
    #     plt.scatter(x.data.numpy(), y.data.numpy())
    #     plt.plot(x.data.numpy(), prediction.data.numpy(), 'r-', lw=5)
    #     plt.text(0.5, 0, 'Loss=%.4f' % loss.data.numpy(), fontdict={'size': 20, 'color': 'red'})
    #     plt.pause(0.1)

plt.scatter(x.data.numpy(), y.data.numpy())
plt.plot(x.data.numpy(), prediction.data.numpy(), 'r-', lw=5)
plt.text(0.5, 0, 'Loss=%.4f' % loss.data.numpy(), fontdict={'size': 20, 'color': 'red'})
plt.ioff()
plt.show()




