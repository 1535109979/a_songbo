import time
from decimal import Decimal, getcontext
getcontext().prec = 4

from binance.spot import Spot as marketClient
import json
import logging
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient


class ClosePosition:
    def __init__(self):
        self.spot_marketclient = marketClient(base_url="https://testnet.binance.vision")
        self.account_client = self.create_order_client(self.on_account)
        self.order_client = self.create_order_client(self.on_order)
        self.illege_list = ['USDT', 'TRY', 'ZAR', 'IDRT', 'JPY', 'UAH', 'BIDR', 'DAI', 'BRL', 'PLN',
                                         'RON', 'ARS']

    def process(self):
        self.account_client.account()

    def get_price(self, symbol):
        price = self.spot_marketclient.ticker_price(symbol)
        return price['price']

    def on_close(self, _):
        logging.info("Do custom stuff when connection is closed")

    def on_order(self, _, message):
        data = json.loads(message)
        print(data)

    def on_account(self, _, message):
        data = json.loads(message)['result']
        balances = data['balances']
        count = 0
        for balance in balances:
            symbol = balance['asset']
            volume = float(balance['free'])
            if volume:
                count += 1
                print(symbol, volume)
                # try:
                #     price = self.get_price(symbol + 'USDT')
                #     print('get price', price)
                # except:
                #     print('Invalid symbol', symbol)
                #     continue
                #
                # send_price = float(price) - 0.0001
                # print(round(send_price, 4))
                # self.send_order(symbol+'USDT', volume, send_price)
                # time.sleep(1)
                # quit()
        print(count)

    def send_order(self, symbol, volume, price):

        self.order_client.new_order(
            id=12345678,
            symbol=symbol,
            side="SELL",
            type="LIMIT",
            timeInForce="GTC",
            quantity=volume,
            price=price,
            newClientOrderId="my_order_id_1",
            newOrderRespType="FULL",
        )

    def create_order_client(self, message_handler):
        api_key = 'uVesQpCYzqOY66PvkpI3a9XTm5Wwhm5oIYtssBDDVuaLyJhPWt1NFsrEFthI1dSh'
        api_secret = 'leeK2goTtYXRlUT4Dj0nPz8SbxmAMFo5ZKkTDpFYFj6FPkVRIEOOHLKJRb2glAcX'
        stream_url = "wss://testnet.binance.vision/ws-api/v3"

        return SpotWebsocketAPIClient(
            stream_url=stream_url,
            api_key=api_key,
            api_secret=api_secret,
            on_message=message_handler,
            on_close=self.on_close,
        )


if __name__ == '__main__':
    ClosePosition().process()

