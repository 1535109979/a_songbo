from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import random
import seaborn as sns

app = Flask(__name__)


@app.route('/')
def index():
    # 创建虚拟数据
    date_range = pd.date_range(start='2023-01-01', periods=100)
    close_prices = [random.uniform(100, 150) for _ in range(100)]
    df = pd.DataFrame({'Close': close_prices}, index=date_range)

    # 应用 Seaborn 样式
    sns.set_style('darkgrid')

    # 创建图表
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='收盘价', color='#007bff', linewidth=2)
    plt.title('虚拟股票收盘价折线图', fontsize=16)
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('收盘价', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.tight_layout()

    # 将图表保存为 PNG 图片
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    # 渲染 HTML 模板 并返回
    return render_template('index.html', plot_url=plot_url) # 这里增加了 return


if __name__ == '__main__':
    app.run(debug=True)
