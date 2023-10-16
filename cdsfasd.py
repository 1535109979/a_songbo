import numpy as np

# 假设有一个包含历史价格的数组
prices = [100, 105, 98, 102, 110, 115]
print(np.diff(prices))

# 计算收益率（每日变化率）
returns = np.diff(prices) / prices[:-1]

# 计算历史波动率
volatility = np.std(returns) * np.sqrt(len(returns))

print("历史波动率:", volatility)
