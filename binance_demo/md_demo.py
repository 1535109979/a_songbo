
import json
import time

from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient


def _on_open(_):
    print("<on_open>")


def _on_close(_):
    print("<on_close>")


def _on_error(_, data):
    print("<on_error> %s" % data)


def _on_message(_, data):
    print("<on_message> data =", data)
    data = json.loads(data)

    if 'kline' == data.get('e'):
        if data.get('k').get('f') > 0:
            print("<on_message> quote =", data['k'])


client = UMFuturesWebsocketClient(
    stream_url="wss://fstream.binance.com",
    # is_combined=True,
    # on_open=_on_open,
    # on_close=_on_close,
    # on_error=_on_error,
    on_message=_on_message
)

client.kline(symbol="BTCUSDT", interval="1m")

while True:
    time.sleep(30)
    break
