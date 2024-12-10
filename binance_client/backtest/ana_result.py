import matplotlib.pyplot as plt
import pandas as pd
import pandas
from sqlalchemy import create_engine, text
from plotly.subplots import make_subplots
import plotly.graph_objects as go
pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)


engine = create_engine('mysql+pymysql://app:6urA&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')

with engine.connect() as conn:
    sql = ("select updated_time,balance, equity,position_pnl from user_account_snapshoot "
           "where account_id = 'binance_f_226_1234567890' order by updated_time;")

    df_226 = pd.read_sql(text(sql), con=conn)

    sql = ("SELECT account_id,instrument,"
           "SUM(profits) AS sum_profits,"
           "SUM(CASE WHEN profits > 0 THEN 1 ELSE 0 END) AS profit_positive_count,"
           "SUM(CASE WHEN profits > 0 THEN profits ELSE 0 END) AS sum_positive_profits,"
           "SUM(CASE WHEN profits < 0 THEN 1 ELSE 0 END) AS profit_negative_count,"
           "SUM(CASE WHEN profits < 0 THEN profits ELSE 0 END) AS sum_negative_profits "
           "FROM trade_info WHERE (account_id IN ('binance_f_226_1234567890') "
           "AND offset_flag = 'close' AND updated_time > '2024-08-13 09:56:52.50') GROUP BY instrument, account_id;")

    df = pd.read_sql(text(sql), con=conn)

    print(df)

df_226.loc[0:824, 'equity'] = df_226.loc[0:824, 'equity'].apply(lambda x: (x-500) / 5000)
va = df_226.loc[824].equity
df_226.loc[1531:,'equity'] = df_226.loc[1531:, 'equity'].apply(lambda x: x-710)

df_226.loc[825:, 'equity'] = df_226.loc[825:, 'equity'].apply(lambda x: (x-2400) / 15000 + va)


fig = make_subplots(
    rows=1, cols=1, shared_xaxes=True, print_grid=False,  # print_grid 设置为 False 以隐藏网格线
    subplot_titles=("净值记录",)  # 修正了原来代码中的括号使用
)

# 定义特定日期
specific_date = pd.to_datetime('2024-09-11 00:00:00')
# 添加一个点和一条垂直线
fig.add_shape(
    type="line",  # 线类型
    x0=specific_date, y0=df_226['equity'].min(),  # 线的起点
    x1=specific_date, y1=df_226['equity'].max(),  # 线的终点
    xref="x", yref="y",
    line=dict(color="red", width=1, dash="dash")  # 线的颜色、宽度和样式
)

fig.add_trace(go.Scatter(
    x=df_226['updated_time'],
    y=df_226['equity'],
    xhoverformat="%Y-%m-%d %H:%M:%S",
    mode="lines",
    name="净值记录"),
    row=1, col=1
)

x_min = df_226['updated_time'].min() - pd.Timedelta(days=0.5)
x_max = df_226['updated_time'].max() + pd.Timedelta(days=0.5)
fig.update_xaxes(range=[x_min, x_max], row=1, col=1)

# 设置布局和配置项
fig.update_layout(
    autosize=True, overwrite=False,
    showlegend=True, legend=dict(traceorder='normal'),

)

# 显示图表
fig.show()

quit()

fig = go.Figure()

fig.add_trace(go.Table(
    header=dict(values=df.columns, fill_color='paleturquoise', align='left'),
    cells=dict(values=[df[col].tolist() for col in df.columns], fill_color='lavender', align='left')
))

# 添加第一个子图的折线图
fig.add_trace(go.Scatter(
    x=pd.to_datetime(df_226['updated_time']),
    y=df_226['equity'],
    xhoverformat="%Y-%m-%d %H:%M:%S",
    mode="lines",
    name="226净值记录"),
)

fig.update_layout(
    height=1000,  # 调整高度以适应内容
    xaxis=dict(domain=[0, 1]),  # 将折线图放在图表的右侧
    yaxis=dict(domain=[0, 0.7])   # 将折线图放在图表的上部
)

# 显示图表
fig.show()
