import akshare as ak
import pandas
import matplotlib.pyplot as plt

data = ak.futures_rule()


# pandas.set_option("expand_frame_repr", False)      #打印数据不折叠
# pandas.set_option("display.max_rows", 2000)        #  最大显示行数
#
# data = ak.get_futures_daily(start_date="20230101", end_date="20230416", market="SHFE")
#
# df_2305 = data[data['symbol']=='RB2305'].reset_index(drop=True)
# df_2306 = data[data['symbol']=='RB2306'].reset_index(drop=True)
# df_2307 = data[data['symbol']=='RB2307'].reset_index(drop=True)
#
# # plt.plot(df_2307['close'])
# # plt.plot(df_2306['close'])
# # plt.plot(df_2305['close'])
#
# cha1 = df_2305['close'] - df_2306['close']
# cha2 = df_2306['close'] - df_2307['close']
#
# plt.plot(cha1 - cha2)
#
# plt.show()



