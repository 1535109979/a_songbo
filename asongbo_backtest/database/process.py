import sqlite3

import pandas as pd
#
# with sqlite3.connect('future_data.db') as conn:
#     df = pd.read_sql('select * from future_daily_data', conn)
#
# print(df)
#
# df.to_csv('future_daily_data.csv', index=False)


import akshare as ak

report_date = '20230930'

df = ak.stock_zcfz_em(date=report_date)
print(df)
df['报告期'] = report_date
df = df.drop('序号', axis=1)

# def process_stock(df_code):
#     print(df_code)
#     quit()
#
#
# df.groupby('股票代码').apply(process_stock)

# with sqlite3.connect('future_data.db') as conn:
#     df.to_sql('finance_data', conn, if_exists='append', index=False)

