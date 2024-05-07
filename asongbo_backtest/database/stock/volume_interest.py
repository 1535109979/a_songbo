import pandas as pd
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt

# plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['font.sans-serif']=['Hiragino Sans GB'] # 修改字体


date = '2024-01-16'
conn = create_engine('mysql+pymysql://app:6uRa&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/'
                         'app?charset=utf8mb4')

sql = (f"select instrument ,volume / open_interest as change_rate from daily_instrument "
       f"where open_interest > 10000 and trading_date = '{date}' "
       f"order by trading_date desc, volume / open_interest desc limit 50")

with conn.connect() as conn:
    df = pd.read_sql(text(sql), conn)

data = [['排名', '合约', '活跃度']]

for i in range(50):
    data.append([i+1, df.loc[i].instrument, round(df.loc[i].change_rate, 2)])

fig, ax = plt.subplots(figsize=(8, 14))

ax.axis('off')
table_title = date + '活跃度排名'
ax.set_title(table_title, fontweight='bold', fontsize=16, y=1.1)

table = ax.table(cellText=data, loc='center')
table.scale(1, 1.5)

table.set_fontsize(14)
for i in range(len(data)):
    for j in range(len(data[0])):
        cell = table[i, j]
        cell.set_text_props(ha='center', va='center')

        if i != 0 and j == 2:
            cell.set_facecolor('lightpink')
        if i != 0 and j == 1:
            cell.set_facecolor('lightyellow')

for j in range(3):
    cell = table.get_celld()[(0, j)]
    cell.set_facecolor('lightblue')
    cell.set_alpha(1)


plt.savefig(f'{date}.png')

