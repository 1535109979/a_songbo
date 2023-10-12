import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv('./data/SHFE_20230501_20230613.csv')
print(df.loc[0])

df_rb2308 = df[df['symbol'] == 'RB2309'].reset_index(drop=True)
df_rb2307 = df[df['symbol'] == 'RB2310'].reset_index(drop=True)
print(df_rb2308)
print(df_rb2307)

df_diff = pd.DataFrame()
df_diff['close_2308'] = df_rb2308['close']
df_diff['close_2307'] = df_rb2307['close']
df_diff['diff'] = df_diff.eval('close_2308 - close_2307')

# plt.plot()
plt.plot(df_diff['diff'])
plt.show()


