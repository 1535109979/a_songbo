#!/usr/bin/env python
import json
import time
import logging
from binance.lib.utils import config_logging
from binance.spot import Spot as Client
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient

api_key = 'uVesQpCYzqOY66PvkpI3a9XTm5Wwhm5oIYtssBDDVuaLyJhPWt1NFsrEFthI1dSh'
api_secret = 'leeK2goTtYXRlUT4Dj0nPz8SbxmAMFo5ZKkTDpFYFj6FPkVRIEOOHLKJRb2glAcX'
stream_url = "wss://testnet.binance.vision"
base_url = "https://testnet.binance.vision"

# api_key = "lfFQPMO2aNVuq6RI8h4PzPObfLQjWsvPcJ8zpfbYb0TJZV3zFmuxTTN7z0aj7lnc"
# api_secret = "9x0h75LjgFw7QwAa7yYFOvDOpN4VKPx4i6iRiicTadZpTLMrTqW4uetm1GSg8srk"
# stream_url = "wss://stream.binance.com:9443"
# base_url = "https://api.binance.com"

config_logging(logging, logging.DEBUG)


def message_handler(_, data):
    print('message_handler', data)


client = Client(api_key, base_url=base_url)
response = client.new_listen_key()

print("Receving listen key : {}".format(response["listenKey"]))

ws_client = SpotWebsocketStreamClient(
    stream_url=stream_url, on_message=message_handler
)

ws_client.user_data(listen_key=response["listenKey"])


