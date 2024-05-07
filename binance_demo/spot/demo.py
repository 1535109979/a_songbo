import logging
import time
import os
import certifi
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient

config_logging(logging, logging.DEBUG)

os.environ['SSL_CERT_FILE'] = certifi.where()


def on_close(_):
    logging.info("Do custom stuff when connection is closed")


def message_handler(_, message):
    logging.info(message)


api_key = "lfFQPMO2aNVuq6RI8h4PzPObfLQjWsvPcJ8zpfbYb0TJZV3zFmuxTTN7z0aj7lnc"
api_secret = "9x0h75LjgFw7QwAa7yYFOvDOpN4VKPx4i6iRiicTadZpTLMrTqW4uetm1GSg8srk"

my_signed_client = SpotWebsocketAPIClient( stream_url="wss://ws-api.binance.com:443/ws-api/v3",
                                           api_key=api_key, api_secret=api_secret,
                                           on_message=message_handler,
                                           on_close=on_close, )

my_signed_client.account()
time.sleep(2)

logging.info("closing ws connection")
my_signed_client.stop()