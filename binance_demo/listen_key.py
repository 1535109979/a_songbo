# import logging
# from binance.lib.utils import config_logging
# from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
#
#
# config_logging(logging, logging.DEBUG)
#
#
# def message_handler(_, message):
#     print(message)
#
#
# ws_client = UMFuturesWebsocketClient(on_message=message_handler)
#
# ws_client.user_data(
#     listen_key='cpavGwwcXGzl1HdaAgaVP17B8LE7gFku3KPm&maIKOJROSZxCKVBgGNDkxZMO7',
#     id=1,
# )

#!/usr/bin/env python
from datetime import datetime
import time
import logging
from binance.lib.utils import config_logging
from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

config_logging(logging, logging.DEBUG)


def message_handler(_, message):
    print(message)


api_key = "lfFQPMO2aNVuq6RI8h4PzPObfLQjWsvPcJ8zpfbYb0TJZV3zFmuxTTN7z0aj7lnc"
client = UMFutures(api_key)
# response = client.new_listen_key()
# print(response)
response = client.renew_listen_key('cpavGwwcXGzl1HdaAgaVP17B8LE7gFku3KPm&maIKOJROSZxCKVBgGNDkxZMO7')
print(response)

# logging.info("Listen key : {}".format(response["listenKey"]))

# ws_client = UMFuturesWebsocketClient(on_message=message_handler)
#
# ws_client.user_data(
#     listen_key=response["listenKey"],
#     id=1,
# )


# while 1:
#     print(datetime.now(), client.ping())
#     time.sleep(30)
