import traceback
from typing import Optional
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
import json
import time

from binance.websocket.websocket_client import BinanceWebsocketClient


class BiFutureMd:
    def __init__(self, gateway):
        self.gateway = gateway
        # 获取柜台配置
        self.configs: dict = gateway.get_api_configs()

        self.client: Optional[UMFuturesWebsocketClient] = None

        # 当前进程登录次数
        self.reqUserLoginId = 0

    @property
    def logger(self):
        return self.gateway.logger

    def connect(self):
        if self.client:
            self.logger.info("服务已连接.")
            return

        self.reqUserLoginId += 1
        self.client = UMFuturesWebsocketClient(
            stream_url=self.configs.get("stream_url"),
            is_combined=self.configs.get("is_combined", False),
            on_open=self._on_open,
            on_close=self._on_close,
            on_error=self._on_error,
            on_message=self._on_message)

        self.logger.info("<create_client> %s %s %s", self.reqUserLoginId, self.client, self.configs)

    def _reconnect(self):
        self.logger.info("<reconnect> %s %s", self.reqUserLoginId, self.client)
        time.sleep(5)
        self.client = None
        self.connect()

    def _on_open(self, _):
        self.logger.info("<on_open> %s %s", self.reqUserLoginId, _)

    def _on_close(self, _):
        self.logger.info("<on_close> %s %s", self.reqUserLoginId, _)
        self.gateway.on_front_disconnected("on_client_close")
        self._reconnect()

    def _on_error(self, _, data):
        self.logger.error("<on_error> %s %s %s", self.reqUserLoginId, _, data)
        self.gateway.on_error(data)

    def _on_message(self, _, data):
        data = json.loads(data)

        if 'kline' == data.get('e'):
            self._on_kline_data(data)

    def _on_kline_data(self, data: dict):
        """ 收到行情
        {
          "e": "kline",     // Event type
          "E": 1638747660000,   // Event time
          "s": "BTCUSDT",    // Symbol
          "k": {
            "t": 1638747660000, // Kline start time
            "T": 1638747719999, // Kline close time
            "s": "BTCUSDT",  // Symbol
            "i": "1m",      // Interval
            "f": 100,       // First trade ID
            "L": 200,       // Last trade ID
            "o": "0.0010",  // Open price
            "c": "0.0020",  // Close price
            "h": "0.0025",  // High price
            "l": "0.0015",  // Low price
            "v": "1000",    // Base asset volume
            "n": 100,       // Number of trades
            "x": false,     // Is this kline closed?
            "q": "1.0000",  // Quote asset volume
            "V": "500",     // Taker buy base asset volume
            "Q": "0.500",   // Taker buy quote asset volume
            "B": "123456"   // Ignore
          }
        }
        """
        k = data['k']
        if not k or k.get('f', 0) <= 0:
            return

        try:
            self.gateway.on_quote(quote={
                "id": int(data["E"]), "localtime": data["E"],
                "symbol": data["s"], "name": k["s"],
                "open_price": k['o'],
                "high_price": k['h'],
                "low_price": k['l'],
                "last_price": k['c'],
                "volume": k['v'],
                "turnover": k['q'],
                "is_closed": 1 if k['x'] else 0,
            })
        except Exception as e:
            traceback.print_exc()
            self.logger.error("<on_message> %s data: %s", e, data)

    def subscribe(self, instrument: list, interval="1m"):
        """ 订阅行情 """
        if not self.client:
            self.logger.error("!!! cannot subscribe !!! client=%s", self.client)
            return False

        for symbol in instrument:
            self.client.kline(symbol=symbol, interval=interval)
            self.logger.info("<subscribe_kline> %s %s", interval, symbol)

            # 订阅过快会导致连接被服务端断开
            time.sleep(0.5)
        return True

    def unsubscribe(self, instrument, interval="1m"):
        """ 取消订阅行情 """
        if not self.client:
            self.logger.error("!!! cannot unsubscribe !!! client=%s", self.client)
            return False

        for symbol in instrument:
            self.client.kline(symbol=symbol, interval=interval,
                              action=BinanceWebsocketClient.ACTION_UNSUBSCRIBE)
            self.logger.info("<unsubscribe_kline> %s %s", interval, symbol)
            time.sleep(0.5)
        return True