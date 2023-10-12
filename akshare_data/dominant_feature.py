import akshare as ak
import matplotlib.pyplot as plt
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
#
# get_spot_price_df = ak.futures_spot_price("20170712")
# print(get_spot_price_df)
# print(get_spot_price_df.loc[0])

# import akshare as ak
# df = ak.get_futures_daily(start_date="20230501", end_date="20230613", market="SHFE")
# print(df)
#
# df.to_csv('./data/SHFE_20230501_20230613.csv')

time_period = '5'

variety = 'rb'
code_a = variety + '2310'
code_b = variety + '2309'
code_c = variety + '2309'

df_a = ak.futures_zh_minute_sina(symbol=code_a, period=time_period)
df_b = ak.futures_zh_minute_sina(symbol=code_b, period=time_period)
df_c = ak.futures_zh_minute_sina(symbol=code_c, period=time_period)

# print(df_a)
# print(df_b)

col = ['datetime','close']
df = pd.merge(df_a[col],df_b[col],how='outer',on='datetime')
# df = pd.merge(df,df_c[col],how='outer',on='datetime')
df = df.dropna()
# print(df)
# quit()
df = df.sort_values(by='datetime').reset_index(drop=True)
df['diff'] = df.eval('close_x - close_y')
print(df)

plt.title(f'{code_a} - {code_b},period = {time_period}')
plt.plot(df['diff'])
plt.show()


