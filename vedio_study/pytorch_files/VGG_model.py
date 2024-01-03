import torch
import torch.nn as nn


class VGGBlock(nn.Module):
    def __init__(self, num_convs, in_channels, out_channels):
        super(VGGBlock, self).__init__()
        layers = []
        for _ in range(num_convs):
            layers += [nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
                       nn.ReLU(inplace=True)]
            in_channels = out_channels
        layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
        self.vgg_block = nn.Sequential(*layers)

    def forward(self, x):
        return self.vgg_block(x)


class VGG(nn.Module):
    def __init__(self, conv_arch):
        super(VGG, self).__init__()
        in_channels = 1
        self.conv_blks = nn.ModuleList()

        for (num_convs, out_channels) in conv_arch:
            self.conv_blks.append(VGGBlock(num_convs, in_channels, out_channels))
            in_channels = out_channels

        self.flatten = nn.Flatten()
        self.fc_layers = nn.Sequential(
            nn.Linear(512 * 7 * 7, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, 10)  # Assuming 10 classes for output
        )

    def forward(self, x):
        for blk in self.conv_blks:
            x = blk(x)
        x = self.flatten(x)
        x = self.fc_layers(x)
        return x


# 定义VGG网络结构
conv_arch = ((1, 64), (1, 128), (2, 256), (2, 512), (2, 512))
net = VGG(conv_arch)

# 生成随机输入
X = torch.randn(size=(10, 1, 224, 224))

# 前向传播
out = net(X)
print(out.shape)
