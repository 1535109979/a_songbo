#!/usr/bin/env python
import logging
import time

from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError

key = "lfFQPMO2aNVuq6RI8h4PzPObfLQjWsvPcJ8zpfbYb0TJZV3zFmuxTTN7z0aj7lnc"
secret = "9x0h75LjgFw7QwAa7yYFOvDOpN4VKPx4i6iRiicTadZpTLMrTqW4uetm1GSg8srk"

hmac_client = UMFutures(key=key, secret=secret)
# # data = hmac_client.account()
# data = hmac_client.exchange_info()
# print(data['rateLimits'])

while 1:
    data = hmac_client.account()
    print(time.time(), data.keys())
    time.sleep(5)


