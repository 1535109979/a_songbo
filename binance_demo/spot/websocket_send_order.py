#!/usr/bin/env python
import json
import logging
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient


config_logging(logging, logging.DEBUG)


def on_close(_):
    logging.info("Do custom stuff when connection is closed")


def message_handler(_, message):
    data = json.loads(message)
    print(data)


api_key = 'uVesQpCYzqOY66PvkpI3a9XTm5Wwhm5oIYtssBDDVuaLyJhPWt1NFsrEFthI1dSh'
api_secret = 'leeK2goTtYXRlUT4Dj0nPz8SbxmAMFo5ZKkTDpFYFj6FPkVRIEOOHLKJRb2glAcX'
stream_url = "wss://testnet.binance.vision/ws-api/v3"

# api_key = "lfFQPMO2aNVuq6RI8h4PzPObfLQjWsvPcJ8zpfbYb0TJZV3zFmuxTTN7z0aj7lnc"
# api_secret = "9x0h75LjgFw7QwAa7yYFOvDOpN4VKPx4i6iRiicTadZpTLMrTqW4uetm1GSg8srk"
# stream_url='wss://ws-api.binance.com:443/ws-api/v3'

my_client = SpotWebsocketAPIClient(
    stream_url=stream_url,
    api_key=api_key,
    api_secret=api_secret,
    on_message=message_handler,
    on_close=on_close,
)

my_client.account()

# my_client.cancel_open_orders('EOSUSDT')

# my_client.get_open_orders()

# my_client.order_history(symbol='LOKAUSDT')
# my_client.get_order(symbol='LOKAUSDT', orderId='')

# my_client.get_order('BTCUSDT', orderId='10349660')


# result = my_client.new_order(
#     id=12345678,
#     symbol="BTCUSDT",
#     side="BUY",
#     type="LIMIT",
#     timeInForce="GTC",
#     quantity=0.002,
#     price=70000,
#     newClientOrderId="my_order_id_1",
#     newOrderRespType="FULL",
# )

# print('result', result)


# volume = 0.24826000



