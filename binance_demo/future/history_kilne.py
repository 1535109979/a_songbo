from datetime import datetime

from binance.um_futures import UMFutures


future_client = UMFutures()

data = future_client.klines('EOSUSDT', '1m', limit=10)
for d in data:
    print(datetime.fromtimestamp(d[0]/1000),d)
