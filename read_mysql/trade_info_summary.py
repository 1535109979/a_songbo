from collections import Counter

import pandas as pd
import pandas
from matplotlib import pyplot as plt
from sqlalchemy import create_engine, text

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)

engine = create_engine('mysql+pymysql://app:6urA&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')
# engine = create_engine('mysql+pymysql://app:W^#&3UM4TiXL^as$@sh-cdb-0aicpi8y.sql.tencentcdb.com:60025/app?charset=utf8mb4')

with engine.connect() as conn:
    sql = ("select account_id, instrument,direction,offset_flag,signal_reason,cover_count,turnover,profits, profit_rate,updated_time "
           "from trade_info where account_id IN ('binance_f_226_1234567890','binance_f_1_0923070819') "
           "AND updated_time > '2024-12-14 09:56:52.50';")

    df = pd.read_sql(text(sql), con=conn)


def plt_pic(account_id,symbol,profit_rate_list):
    values = []
    value = 0
    values.append(value)
    for profit in profit_rate_list:
        value += profit
        values.append(value)

    plt.plot(values)
    plt.title(symbol)
    plt.savefig(f'result/{account_id}_{symbol}.jpg')
    plt.clf()

def process_instrument(df_instrument):
    cover_list = []
    df_instrument = df_instrument.sort_values(by=['updated_time']).reset_index(drop=True)
    symbol = df_instrument.loc[0].instrument
    account_id = df_instrument.loc[0].account_id
    profit_rate_list = df_instrument[df_instrument['offset_flag'].isin(['CLOSE', 'SRTOP_PROFIT'])]['profits'].tolist()
    plt_pic(account_id, symbol, profit_rate_list)
    for index, row in df_instrument.iterrows():
        if row['signal_reason'] == 'COVER':
            cover_list.append(row['cover_count'])

    sum_profit = df_instrument['profits'].sum()

    positive_count = df_instrument['profits'][df_instrument['profits'] > 0].count()
    positive_profit = df_instrument['profits'][df_instrument['profits'] > 0].sum()
    negative_count = df_instrument['profits'][df_instrument['profits'] < 0].count()
    negative_profit = df_instrument['profits'][df_instrument['profits'] < 0].sum()

    return round(sum_profit, 2), Counter(cover_list), positive_count, negative_count, positive_profit, negative_profit


df_res = df.groupby(['account_id','instrument']).apply(process_instrument).reset_index()
df_res.columns = ['account_id','instrument','data']
df_res[['sum_profit', 'cover', 'positive_count','negative_count', 'positive_profit', 'negative_profit']] = df_res['data'].apply(pd.Series)
df_res = df_res.drop('data', axis=1)
print(df_res)


