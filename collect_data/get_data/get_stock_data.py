import json

import pandas as pd
import requests

import akshare as ak

stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="sz159845", period="daily", start_date="20170301", end_date='20240528', adjust="hfq")
print(stock_zh_a_hist_df)
quit()


# url = ('https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_sh000300_60_1732001522597=/CN_MarketDataService.getKLineData?'
#        'symbol=sh000300&scale=60&ma=no&datalen=1023')

symbol = 'sz159845'

url = (f"https://cn.finance.sina.com.cn/minline/getMinlineData?"
       f"symbol={symbol}&callback=var%20t1sz159845=&version=7.11.0&dpc=1")


r = requests.get(url)
data_text = r.text
data_json = json.loads(data_text.split("=(")[1][:-1])['result']['data']
print(type(data_json),data_json)

df = pd.DataFrame(data_json)

print(df)


