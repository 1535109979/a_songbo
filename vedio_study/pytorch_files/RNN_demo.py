import torch
import torch.nn as nn
import torch.optim as optim
import string
import random


# 定义 RNN 模型
class SimpleRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleRNN, self).__init__()
        self.hidden_size = hidden_size
        self.rnn = nn.RNN(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x, hidden):
        out, hidden = self.rnn(x, hidden)
        out = self.fc(out)
        return out, hidden


# 准备数据
all_characters = string.printable
n_characters = len(all_characters)


def generate_random_sequence(length=20):
    return ''.join(random.choice(all_characters) for _ in range(length))


def char_to_tensor(char):
    return torch.tensor([all_characters.index(char)])


def string_to_tensor(string):
    return torch.tensor([all_characters.index(char) for char in string])


# 构建模型
input_size = n_characters
hidden_size = 50
output_size = n_characters
model = SimpleRNN(1, hidden_size, output_size)

# 定义损失函数和优化器
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)


# 训练模型
def train_model(model, input_tensor, target_tensor):
    hidden = None
    model.zero_grad()
    loss = 0

    for i in range(input_tensor.size(1)):
        output, hidden = model(input_tensor[:, i].unsqueeze(1).float(), hidden)
        loss += criterion(output.squeeze(1), target_tensor[:, i])

    loss.backward()
    optimizer.step()

    return loss.item()


# 进行训练
num_epochs = 1000
for epoch in range(num_epochs):
    input_sequence = generate_random_sequence(10)
    target_sequence = input_sequence[1:] + input_sequence[0]

    input_tensor = string_to_tensor(input_sequence)
    target_tensor = string_to_tensor(target_sequence)

    loss = train_model(model, input_tensor.unsqueeze(0), target_tensor.unsqueeze(0))

    if epoch % 100 == 0:
        print(f'Epoch {epoch}, Loss: {loss}')


# 使用训练好的模型生成文本
def generate_text(model, start_string="A", length=50):
    input_tensor = string_to_tensor(start_string)
    hidden = None
    output_text = start_string

    for i in range(length):
        output, hidden = model(input_tensor.unsqueeze(0).float(), hidden)
        predicted_char = all_characters[torch.argmax(output.squeeze(1)).item()]
        output_text += predicted_char
        input_tensor = char_to_tensor(predicted_char)

    return output_text


generated_text = generate_text(model, start_string="A", length=100)
print("Generated Text:")
print(generated_text)
