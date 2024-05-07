import sqlite3

import pandas as pd


def read_index():
    with sqlite3.connect('../future_data.db') as conn:
        df_index = pd.read_sql('select * from stock_index', conn)

    df_index['change_rate'] = (df_index['close'] / df_index['close'].shift(1) - 1) * 100
    return df_index[['date', 'change_rate']]


df_index = read_index()

with sqlite3.connect('../future_data.db') as conn:
    df_stock_data = pd.read_sql('select * from stock_daily_data', conn)

df_stock = df_stock_data[['日期', '收盘', '涨跌幅', 'code']]
df_stock.columns = ['date', 'close', 'change_rate', 'code']

df_result = pd.DataFrame(columns=['code', 'diff_sum', 'var'])


def process_stock(df_one):
    if len(df_one) > 20:
        df_one = df_one.reset_index(drop=True)
        code = df_one.loc[0].code
        df = pd.merge(df_one, df_index, how='inner', on='date')
        df['diff'] = df.eval('change_rate_x - change_rate_y')

        tail20_sum = df.tail(20)['diff'].sum()
        tail20_var = df.tail(20)['diff'].var()
        df_result.loc[len(df_result)] = [code, tail20_sum, tail20_var]


df_stock.groupby('code').apply(process_stock)

df_result['score'] = df_result.eval('diff_sum - var*20')
df_result = df_result.sort_values(by='score', ascending=False)
print(df_result)

df_result.to_csv('stock_index_diff.csv', index=False)


