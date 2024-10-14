import json
import time
from datetime import datetime

import numpy as np

from song_binance_client.utils.aio_timer import AioTimer
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient


class MarketDataCollect:

    def __init__(self):
        self.client = UMFuturesWebsocketClient(
            stream_url="wss://fstream.binance.com",
            on_message=self.on_message
        )

        self.data_dict = {}
        self.res = {}

    def run(self):
        self.client.partial_book_depth(symbol="NFPUSDT")
        time.sleep(0.2)
        self.client.partial_book_depth(symbol="RLCUSDT")
        time.sleep(0.2)
        self.client.partial_book_depth(symbol="LTCUSDT")
        time.sleep(0.2)
        self.client.partial_book_depth(symbol="EOSUSDT")
        time.sleep(0.2)
        self.client.partial_book_depth(symbol="AEVOUSDT")
        time.sleep(0.2)
        self.client.partial_book_depth(symbol="APEUSDT")
        time.sleep(0.2)
        self.client.partial_book_depth(symbol="BANDUSDT")
        time.sleep(0.2)
        self.client.partial_book_depth(symbol="CELRUSDT")
        time.sleep(0.2)
        self.client.partial_book_depth(symbol="PORTALUSDT")
        time.sleep(0.2)
        self.client.partial_book_depth(symbol="ONDOUSDT")
        time.sleep(0.2)
        self.client.partial_book_depth(symbol="MOVRUSDT")
        self._add_check_md_timer(5)

    def on_message(self, _, data):
        data = json.loads(data)
        if not data.get('s'):
            return

        symbol = data['s']
        bids = [float(x[0]) * float(x[1]) for x in data['b']]
        asks = [float(x[0]) * float(x[1]) for x in data['a']]
        if self.data_dict.get(symbol):
            self.data_dict[symbol]['bids'].append(bids)
            self.data_dict[symbol]['asks'].append(asks)
        else:
            self.data_dict[symbol] = {'bids': [], 'asks': []}
            self.data_dict[symbol]['bids'].append(bids)
            self.data_dict[symbol]['asks'].append(asks)

    def _add_check_md_timer(self, interval):
        def _func():
            self.cal_mean()
            self._add_check_md_timer(interval)

        AioTimer.new_timer(_delay=interval, _func=_func)

    def cal_mean(self):
        for symbol, d in self.data_dict.items():
            bid_mean = np.mean(np.array(d['bids']), axis=0)
            ask_mean = np.mean(np.array(d['asks']), axis=0)
            print(symbol)
            with open('market_depth.csv', mode='a', newline='') as f:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f'{now_str}, {symbol}, bids,' + ' ,'.join([str(x) for x in bid_mean]) + '\n')
                f.write(f'{now_str}, {symbol}, asks,' + ' ,'.join([str(x) for x in ask_mean]) + '\n')
            self.data_dict[symbol] = {'bids': [], 'asks': []}


if __name__ == '__main__':
    MarketDataCollect().run()

    while 1:
        pass
