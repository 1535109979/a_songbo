#!/usr/bin/env python

import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging
from binance.error import ClientError

# config_logging(logging, logging.DEBUG)

# api_key = 'uVesQpCYzqOY66PvkpI3a9XTm5Wwhm5oIYtssBDDVuaLyJhPWt1NFsrEFthI1dSh'
# api_secret = 'leeK2goTtYXRlUT4Dj0nPz8SbxmAMFo5ZKkTDpFYFj6FPkVRIEOOHLKJRb2glAcX'

api_key = 'ywdKhfbj3jahoM5mE8PhWRbwHReIg8RSvshbcLCp7fhvCVm7MFgfbCuIrmH9szme'
api_secret = 'C2Vp9MKXwjHY4pkFQEN99SDnHDVRjN4Bd31Eq5FPxqnMUxdfCvrUE0QRPKYir5V7'

params = {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "LIMIT",
    "timeInForce": "GTC",
    "quantity": 0.002,
    "price": 70000,
}

client = Client(api_key, api_secret, base_url="https://testnet.binance.vision")

response = client.account()
# response = client.new_order(**params)
# response = client.get_orders('LDOUSDT')

# response = client.get_open_orders('BTCUSDT')
# response = client.cancel_open_orders('BTCUSDT')

print(response)
