import sqlite3
from datetime import datetime

import akshare as ak


col_name = ['代码', '名称', '最新价', '涨跌幅', '成交量', '成交额', '换手率', '市盈率-动态', '市净率', '总市值', '流通市值']
col = ['code', 'name', 'latest_price', 'change', 'volume', 'turnover', 'turnover_rate', 'pe', 'pb',
       'market_value', 'circulation_market_value']

data = ak.stock_sh_a_spot_em()
df = data[col_name]
df.columns = col
df['date'] = datetime.now().strftime('%Y%m%d')
df['exchange'] = 'sh'

with sqlite3.connect('../future_data.db') as conn:
    df.to_sql('all_stock', con=conn, index=False, if_exists='append')


data = ak.stock_sz_a_spot_em()
df = data[col_name]
df.columns = col
df['date'] = datetime.now().strftime('%Y%m%d')
df['exchange'] = 'sz'

with sqlite3.connect('../future_data.db') as conn:
    df.to_sql('all_stock', con=conn, index=False, if_exists='append')
