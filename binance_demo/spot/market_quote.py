#!/usr/bin/env python

from binance.spot import Spot as Client

spot_client = Client(base_url="https://testnet.binance.vision")

price = spot_client.ticker_price("CVXUSDT")

print(price)

