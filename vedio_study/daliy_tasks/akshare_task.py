import json

import akshare as ak
import pandas as pd
import requests


symbol = 'sh600519'
f = '1'
url = f'https://quotes.sina.cn/cn/api/openapi.php/CN_MinlineService.getMinlineData?symbol={symbol}&callback=var%20t1sh600519=&dpc={f}'

r = requests.get(url)
data_text = r.text
data_json = json.loads(data_text.split("=(")[1].split(")")[0])
print(data_json['data'])
# temp_df = pd.DataFrame(data_json)
# print(temp_df)

