import logging
import time
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

def message_handler(_, message):
    logging.info(message)

my_client = UMFuturesWebsocketClient(on_message=message_handler)

# Subscribe to a single symbol stream
my_client.kline(symbol="bnbusdt")
time.sleep(5)
logging.info("closing ws connection")
my_client.stop()

