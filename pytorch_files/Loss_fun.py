import torch
import torch.nn as nn


class CustomLoss(nn.Module):
    def __init__(self):
        super(CustomLoss, self).__init__()

    def forward(self, predicted, target):
        # 计算平方损失
        loss = torch.mean((predicted - target)**2)
        return loss


# 示例使用
# 假设 predicted 和 target 是模型输出和目标值的张量
predicted = torch.randn(10, requires_grad=True)
target = torch.randn(10)

# 创建自定义损失函数实例
custom_loss = CustomLoss()

loss_value = custom_loss(predicted, target)

print(loss_value.item())
