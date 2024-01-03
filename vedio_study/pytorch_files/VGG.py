import torch
from torch import nn


def vgg_block(num_convs, in_channels, out_channels):
    layers = []

    for _ in range(num_convs):
        layers.append(nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1))
        layers.append(nn.ReLU())

        in_channels = out_channels

    layers.append(nn.MaxPool2d(kernel_size=2, stride=2))
    return nn.Sequential(*layers)


conv_arch = ((1, 64), (1, 128), (2, 256), (2, 512), (2, 512))


def vgg(conv_arch):
    in_channels = 1
    conv_blks = []

    for (num_convs, out_channels) in conv_arch:
        conv_blks.append(vgg_block(num_convs, in_channels, out_channels))
        in_channels = out_channels

    return nn.Sequential(*conv_blks, nn.Flatten(),
                         nn.Linear(in_channels * 7 * 7, 4096), nn.ReLU(),
                         nn.Dropout(0.5), nn.Linear(4096, 4096), nn.ReLU(),
                         nn.Dropout(0.5), nn.Linear(4096, 10)
                         )


net = vgg(conv_arch)

print(net)

X = torch.randn(size=(10, 1, 224, 224))

out = net(X)
print(out.shape)

for blk in net:
    X = blk(X)
    print(blk.__class__.__name__, 'output shape:\t', X.shape)


