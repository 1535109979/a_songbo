import re
from collections import defaultdict
from datetime import datetime

from a_songbo.vn.data.process_sqlite import SqliteDatabaseManage, HistoryPrice

last_price = defaultdict(dict)
last_price['rb2311C4111'] = {'quote_time': 1223, 'LastPrice': 1223}
last_price['rb2311P4111'] = {'quote_time': 12, 'LastPrice': 1223}

saved_price = {k: {'price': round(float(v['LastPrice']), 2), 'timestamp': v['quote_time']}
                                    for k, v in last_price.items()}

price_save_list = []
for instrument, value in saved_price.items():
    price_save_list.append({
        'instrument': instrument,
        'price': value['price'],
        'timestamp': value['timestamp'],
    })
with SqliteDatabaseManage().get_connect().atomic():
    HistoryPrice.delete().execute()
    HistoryPrice.insert_many(price_save_list).execute()



# import numpy as np
#
# # 假设有一个包含历史价格的数组
# prices = [100, 105, 98, 102, 110, 115]
# print(np.diff(prices))
#
# # 计算收益率（每日变化率）
# returns = np.diff(prices) / prices[:-1]
#
# # 计算历史波动率
# volatility = np.std(returns) * np.sqrt(len(returns))
#
# print("历史波动率:", volatility)



