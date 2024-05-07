import akshare as ak
import matplotlib.pyplot as plt
import pandas

pandas.set_option("expand_frame_repr", False)      #打印数据不折叠
pandas.set_option("display.max_rows", 2000)

# # df = ak.index_stock_cons_weight_csindex(symbol="000300")
# df = ak.index_stock_cons_weight_csindex(symbol="399905")
# # print(df[['指数代码', '成分券名称', '权重']])
# print(df.loc[0])


# df = ak.futures_main_sina(symbol="IC0", start_date="20200101", end_date="20220101")
# df['pct_change'] = df['收盘价'].pct_change()
# print(df)
# print(df['pct_change'].idxmin())

# plt.plot(df['pct_change'])
# plt.show()

