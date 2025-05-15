import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
df = pd.read_csv('value_result.csv',
                 names=['code', 'cover_rate', 'stop_profit_rate', 'max_count', 'max_value', 'trade_times', 'value',
                        'common_value'])
codes = df['code'].unique()

print(len(codes))

# 获取所有唯一的cover_rate
unique_cover_rates = df['cover_rate'].unique()

# 为每个cover_rate绘制箱体图
for cover_rate in unique_cover_rates:
    # 筛选出当前cover_rate的数据
    subset = df[df['cover_rate'] == cover_rate]

    # 按stop_profit_rate分组
    grouped = subset.groupby('stop_profit_rate')

    # 准备数据
    common_value_data = [group['common_value'].tolist() for _, group in grouped]
    stop_profit_rates = list(grouped.groups.keys())
    trade_times_means = [group['trade_times'].mean() for _, group in grouped]

    # 绘制箱体图
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()  # 创建共享x轴但具有独立y轴的第二个坐标轴

    # 绘制箱体图
    boxplot = ax1.boxplot(common_value_data, showmeans=True, positions=range(len(stop_profit_rates)))

    # 获取均值点的坐标
    means = [float(f.get_ydata()[0]) for f in boxplot['means']]

    # 在箱体图的均值位置添加文本标签
    for i, mean in enumerate(means):
        ax1.text(i, mean, f'{mean:.4f}', ha='center', va='bottom', color='blue', fontsize=9)

    # 绘制trade_times的均值折线图
    ax2.plot(range(len(stop_profit_rates)), trade_times_means, marker='o', color='red', label='Mean trade_times')

    # 设置x轴刻度标签
    ax1.set_xticks(range(len(stop_profit_rates)))
    ax1.set_xticklabels(stop_profit_rates)

    # 设置标题和标签
    ax1.set_title(f'Boxplot of common_value for cover_rate = {cover_rate}')
    ax1.set_xlabel('stop_profit_rate')
    ax1.set_ylabel('common_value', color='blue')
    ax2.set_ylabel('Mean trade_times', color='red')

    # 添加图例
    ax2.legend(loc='upper right')

    # 显示图表
    plt.savefig(f'ana_result/{cover_rate}.jpg')
    plt.clf()
    # plt.show()