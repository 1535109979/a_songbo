#!/usr/bin/env python
import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError

config_logging(logging, logging.DEBUG)

key = "lfFQPMO2aNVuq6RI8h4PzPObfLQjWsvPcJ8zpfbYb0TJZV3zFmuxTTN7z0aj7lnc"
secret = "9x0h75LjgFw7QwAa7yYFOvDOpN4VKPx4i6iRiicTadZpTLMrTqW4uetm1GSg8srk"

um_futures_client = UMFutures(key=key, secret=secret)


req = {'newOrderRespType': 'RESULT',
       'newClientOrderId': 'x-NEUC93TV1675Z6ZFJ3290021',
       'symbol': 'BTCUSDT',
       'side': 'BUY',
       'positionSide': 'LONG',
       'price': 63000,
       'type': 'LIMIT',
        'timeInForce': 'GTC',
       'quantity': 0.002
       }

# req = {'newClientOrderId': 'x-NEUC93TV71XVX315000002',
#        'newOrderRespType': 'FULL',
#        'positionSide': 'LONG',
#        'price': 67000,
#        'quantity': 1.042,
#        'side': 'SELL',
#        'symbol': 'LTCUSDT',
#        'timeInForce': 'GTC',
#        'type': 'LIMIT'}

try:
    response = um_futures_client.new_order(**req)

    logging.info(response)
except ClientError as error:
    logging.error(
        "Found error. status: {}, error code: {}, error message: {}".format(
            error.status_code, error.error_code, error.error_message
        )
    )