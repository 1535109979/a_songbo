from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine, text


engine = create_engine('mysql+pymysql://app:6urA&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')

with engine.connect() as conn:
    sql = ("select updated_time,balance, equity,position_pnl from user_account_snapshoot "
           "where account_id = 'binance_f_226_1234567890' and updated_time > '2024-08-13 07:36:52.50' "
           "order by updated_time;")

    df_226 = pd.read_sql(text(sql), con=conn)
    sql = ("select updated_time,balance, equity,position_pnl from user_account_snapshoot "
           "where account_id = 'binance_f_1_0923070819' and updated_time > '2024-08-13 07:36:52.50' "
           "order by updated_time;")
    df_1 = pd.read_sql(text(sql), con=conn)

df_1['updated_time'] = pd.to_datetime(df_1['updated_time'])
df_226['updated_time'] = pd.to_datetime(df_226['updated_time'])
print(df_1)

x_min = df_1['updated_time'].min() - pd.Timedelta(days=0.5)
x_max = df_1['updated_time'].max() + pd.Timedelta(days=0.5)

fig = make_subplots(
    rows=2, cols=1, shared_xaxes=True, print_grid=False,  # print_grid 设置为 False 以隐藏网格线
    subplot_titles=("1净值记录", "226净值记录")  # 修正了原来代码中的括号使用
)

fig.update_xaxes(range=[x_min, x_max], row=1, col=1)


fig.add_trace(go.Scatter(
    x=df_1['updated_time'],
    y=df_1['equity'],
    xhoverformat="%Y-%m-%d %H:%M:%S",
    mode="lines",
    name="1净值记录"),
    row=1, col=1
)

# 添加第二个 DataFrame 的折线图
fig.add_trace(go.Scatter(
    x=df_226['updated_time'],
    y=df_226['equity'],
    xhoverformat="%Y-%m-%d %H:%M:%S",
    mode="lines",
    name="226净值记录"),
    row=2, col=1
)

# 设置布局和配置项
fig.update_layout(
    # margin=dict(
    #     l=100,  # 左边距
    #     r=100,  # 右边距
    #     t=50,   # 上边距
    #     b=50,   # 下边距
    # ),
    autosize=True, overwrite=False,
    showlegend=True, legend=dict(traceorder='normal'),

)

# 显示图表
fig.show()

