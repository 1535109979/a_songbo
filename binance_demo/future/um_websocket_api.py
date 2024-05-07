import json
import logging
import time

from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

from byt_common.concurrent.aio_timer import AioTimer
from byt_common.enums.exchange_enum import OrderPriceType, OffsetFlag, Direction
# from byt_trading_vn.src.trade.bian_future.do.rtn_order import RtnOrder
# from do.account import AccountBook

config_logging(logging, logging.DEBUG)


order_direction_map = {
    (OffsetFlag.OPEN, Direction.LONG): ('BUY', 'LONG'),
    (OffsetFlag.CLOSE, Direction.LONG): ('SELL', 'LONG'),
    (OffsetFlag.OPEN, Direction.SHORT): ('SELL', 'SHORT'),
    (OffsetFlag.CLOSE, Direction.SHORT): ('BUY', 'SHORT'),
}


class UMFutureApi:

    def __init__(self):
        key = "lfFQPMO2aNVuq6RI8h4PzPObfLQjWsvPcJ8zpfbYb0TJZV3zFmuxTTN7z0aj7lnc"
        secret = "9x0h75LjgFw7QwAa7yYFOvDOpN4VKPx4i6iRiicTadZpTLMrTqW4uetm1GSg8srk"
        self.client = UMFutures(key=key, secret=secret)
        self.listen_client = None

        self.order_id_map = {}
        # self.account_book = AccountBook(account_id='sdfasdf')

    def connect(self):
        # self.query_exchange_info()

        self.query_account()
        # listen_key = self.create_listen_key()
        # self.listen_use_data(listen_key)

    def query_exchange_info(self):
        """
        :return:
        dict_keys(['timezone', 'serverTime', 'futuresType', 'rateLimits', 'exchangeFilters', 'assets', 'symbols'])
        """
        data = self.client.exchange_info()

        # order_limit_data = data['symbols'][0]
        # print(order_limit_data)

        for symbol_data in data['symbols']:
            self.account_book.set_instrument_books(symbol_data)

    def create_listen_key(self):
        # 建议大约每 60 分钟发送一次 ping。如果响应-1125错误“此listenKey不存在。
        # 重新创建listenKey并使用新的listenKey来建立连接。
        response = self.client.new_listen_key()
        return response['listenKey']

    def listen_use_data(self, listen_key):
        self.listen_client = UMFuturesWebsocketClient(on_message=self.on_use_data)
        self.listen_client.user_data(
            listen_key=listen_key,
            id=1,
        )

    def on_use_data(self, _, message):
        message = json.loads(message)
        # print('---on_use_data---', message)

        if message.get('e') == "ACCOUNT_CONFIG_UPDATE":
            """
            {'e': 'ACCOUNT_CONFIG_UPDATE', 'T': 1709885288567, 'E': 1709885288567, 
            'ac': {'s': 'BTCUSDT', 'l': 1}}
            """
            symbol = message['ac']['s']
            levalage = message['ac']['l']

        if message.get('e') == "ACCOUNT_UPDATE":
            """
            {'e': 'ACCOUNT_UPDATE', 'T': 1709882603823, 'E': 1709882603823, 
            'a': {'B': [{'a': 'USDT', 'wb': '400.57057938', 'cw': '400.57057938', 'bc': '-17'}], 
            'P': [], 'm': 'WITHDRAW'}}
            """
            for asset in message['a']['B']:
                if asset['a'] == 'USDT':
                    self.account_book.update_avil(asset['wb'])

        if message.get('e') == "ORDER_TRADE_UPDATE":
            client_order_id = message['o']['c']
            if self.order_id_map.get(client_order_id):
                rtn_order = self.order_id_map[client_order_id]
                if rtn_order:
                    rtn_order.update_by_order_trade_update(message)
                    self.account_book.update_by_order_rtn(rtn_order)

        print('on_use_data avail:', self.account_book.avail)

    def query_account(self):
        """
        :return:  dict
        feeTier: 用户的手续费等级。
        canTrade: 表示账户是否允许交易。
        canDeposit: 表示账户是否允许存款。
        canWithdraw: 表示账户是否允许提款。
        tradeGroupId: 交易组 ID，用于识别用户所在的交易组。
        updateTime: 数据更新的时间戳。
        multiAssetsMargin: 多资产保证金模式。
        totalInitialMargin: 总初始保证金。
        totalMaintMargin: 总维持保证金。
        totalWalletBalance: 总钱包余额。
        totalUnrealizedProfit: 总未实现盈亏。
        totalMarginBalance: 总保证金余额。
        totalPositionInitialMargin: 总仓位初始保证金。
        totalOpenOrderInitialMargin: 总挂单初始保证金。
        totalCrossWalletBalance: 总跨钱包余额。
        totalCrossUnPnl: 总跨未实现盈亏。
        availableBalance: 可用余额。
        maxWithdrawAmount: 最大可提取金额。
        assets: 账户中的资产信息。
        positions: 账户中的仓位信息。
        """
        response = self.client.account()

        self.account_book.update_by_data(response)

        for k, v in response.items():
            if k == 'assets':
                for assect in v:
                    if assect.get('asset') == 'USDT':
                        if self.account_book.avail != assect.get('walletBalance'):
                            self.account_book.avail = assect.get('walletBalance')
                        break

            if k == 'positions':
                for position_data in v:
                    # print(position_data)
                    # if not float(position_data.get('positionAmt')):
                    #     continue
                    instrument = position_data.get('symbol')
                    direction = position_data.get('positionSide')
                    position = self.account_book.get_instrument_position(instrument, direction)
                    position.update_data(position_data)
                    position.__post_init__()

        print('query_account avil', self.account_book.avail)

    def query_leverage_brackets(self):
        # 杠杆分层标准
        """
        :return:
        [{'symbol': 'BTCUSDT',
        'brackets': [{'bracket': 1, 'initialLeverage': 125, 'notionalCap': 50000, 'notionalFloor': 0,
        'maintMarginRatio': 0.004, 'cum': 0.0},
                    {'bracket': 2, 'initialLeverage': 100, 'notionalCap': 500000, 'notionalFloor': 50000,
        'maintMarginRatio': 0.005, 'cum': 50.0},
                    {'bracket': 3, 'initialLeverage': 50, 'notionalCap': 10000000, 'notionalFloor': 500000,
        'maintMarginRatio': 0.01, 'cum': 2550.0},
                    {'bracket': 4, 'initialLeverage': 20, 'notionalCap': 80000000, 'notionalFloor': 10000000,
        'maintMarginRatio': 0.025, 'cum': 152550.0},
                    {'bracket': 5, 'initialLeverage': 10, 'notionalCap': 150000000, 'notionalFloor': 80000000,
        'maintMarginRatio': 0.05, 'cum': 2152550.0},
                    {'bracket': 6, 'initialLeverage': 5, 'notionalCap': 300000000, 'notionalFloor': 150000000,
        'maintMarginRatio': 0.1, 'cum': 9652550.0},
                    {'bracket': 7, 'initialLeverage': 4, 'notionalCap': 450000000, 'notionalFloor': 300000000,
        'maintMarginRatio': 0.125, 'cum': 17152550.0},
                    {'bracket': 8, 'initialLeverage': 3, 'notionalCap': 600000000, 'notionalFloor': 450000000,
        'maintMarginRatio': 0.15, 'cum': 28402550.0},
                    {'bracket': 9, 'initialLeverage': 2, 'notionalCap': 800000000, 'notionalFloor': 600000000,
        'maintMarginRatio': 0.25, 'cum': 88402550.0},
                    {'bracket': 10, 'initialLeverage': 1, 'notionalCap': 1000000000, 'notionalFloor': 800000000,
        'maintMarginRatio': 0.5, 'cum': 288402550.0}]}]
        """
        self.client.leverage_brackets(symbol="BTCUSDT")

    def change_leverage(self):
        # 调整杠杆倍数
        """
        :return:
        {'symbol': 'BTCUSDT', 'leverage': 2, 'maxNotionalValue': '800000000'}
        """
        response = self.client.change_leverage(symbol="BTCUSDT", leverage=1)
        print(response)

    def send_order(self, symbol='BTCUSDT', order_price_type=OrderPriceType.FAK, offset_flag=OffsetFlag.OPEN,
                   direction=Direction.LONG, volume=0.002, price=67400):
        """
        {'orderId': 281081863136, 'symbol': 'BTCUSDT', 'status': 'NEW', 'clientOrderId': 'VlZWACgj11alA4mZM7AphV',
        'price': '66008.00', 'avgPrice': '0.00', 'origQty': '0.002', 'executedQty': '0.000', 'cumQty': '0.000',
        'cumQuote': '0.00000', 'timeInForce': 'GTC', 'type': 'LIMIT', 'reduceOnly': False, 'closePosition': False,
        'side': 'BUY', 'positionSide': 'LONG', 'stopPrice': '0.00', 'workingType': 'CONTRACT_PRICE',
        'priceProtect': False, 'origType': 'LIMIT', 'priceMatch': 'NONE', 'selfTradePreventionMode': 'NONE',
        'goodTillDate': 0, 'updateTime': 1709798915926}
        """

        client_order_id = ''

        side, positionSide = order_direction_map[(offset_flag, direction)]

        if order_price_type == OrderPriceType.LIMIT:
            req = {
                'symbol': symbol,
                'side': side,
                'positionSide': positionSide,
                'type': 'LIMIT',
                'quantity': volume,
                'price': price,
                'timeInForce': "GTC",
                # 'newClientOrderId': client_order_id,
            }

        if order_price_type == OrderPriceType.FAK:
            """
            {'orderId': 281748353111, 'symbol': 'BTCUSDT', 'status': 'NEW', 'clientOrderId': 'y0NTZZK24wlrCiBrSuLHtp', 
            'price': '66000.00', 'avgPrice': '0.00', 'origQty': '0.002', 'executedQty': '0.000', 'cumQty': '0.000', 
            'cumQuote': '0.00000', 'timeInForce': 'IOC', 'type': 'LIMIT', 'reduceOnly': False, 'closePosition': False, 
            'side': 'BUY', 'positionSide': 'LONG', 'stopPrice': '0.00', 'workingType': 'CONTRACT_PRICE', 
            'priceProtect': False, 'origType': 'LIMIT', 'priceMatch': 'NONE', 'selfTradePreventionMode': 'NONE', 
            'goodTillDate': 0, 'updateTime': 1709875725667}
            """
            req = {
                'symbol': symbol,
                'side': side,
                'positionSide': positionSide,
                'type': 'LIMIT',
                'quantity': volume,
                'price': price,
                'timeInForce': "IOC",
                # 'newClientOrderId': order_id,
            }

        # print('--req---', req)
        response = self.client.new_order(**req)
        # print('---response---', response)

        rtn_order = RtnOrder.create_by_order_data(response)
        rtn_order.__post_init__()

        # print('---rtn_order---', rtn_order.__dict__)

        self.order_id_map[rtn_order.client_order_id] = rtn_order

    def cancel_order(self, symbol='BTCUSDT', orderId=None, order_client_id=None):
        response = self.client.cancel_order(symbol, orderId, order_client_id)
        print(response)

    def cancel_all_open_order(self, symbol='BTCUSDT'):
        response = self.client.cancel_open_orders(symbol)
        print(response)

    def query_position_mode(self):
        """
        :return:
        {'dualSidePosition': True}
        """
        response = self.client.get_position_mode()
        print(response)

    def change_position_mode(self):
        response = self.client.change_position_mode(dualSidePosition="true")
        print(response)

    def query_order(self):
        """
        {'orderId': 281081863136, 'symbol': 'BTCUSDT', 'status': 'CANCELED', 'clientOrderId': 'VlZWACgj11alA4mZM7AphV',
        'price': '66008.00', 'avgPrice': '0.00', 'origQty': '0.002', 'executedQty': '0.000', 'cumQuote': '0.00000',
        'timeInForce': 'GTC', 'type': 'LIMIT', 'reduceOnly': False, 'closePosition': False, 'side': 'BUY',
        'positionSide': 'LONG', 'stopPrice': '0.00', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False,
        'origType': 'LIMIT', 'priceMatch': 'NONE', 'selfTradePreventionMode': 'NONE', 'goodTillDate': 0,
        'time': 1709798915926, 'updateTime': 1709798929758}
        """
        response = self.client.query_order(symbol='BTCUSDT', orderId='281081863136')
        print(response)

    def query_orders(self):
        # 当前委托
        response = self.client.get_orders()
        print(response)

    def query_all_orders(self, symbol='BTCUSDT'):
        response = self.client.get_all_orders(symbol)
        print(response)

    def query_account_trades(self, symbol='BTCUSDT'):
        response = self.client.get_account_trades(symbol)
        print(response)

    def query_position_risk(self):
        """
        {'symbol': 'SNTUSDT', 'positionAmt': '0', 'entryPrice': '0.0', 'breakEvenPrice': '0.0', 'markPrice': '0.00000000',
        'unRealizedProfit': '0.00000000', 'liquidationPrice': '0', 'leverage': '20', 'maxNotionalValue': '25000',
        'marginType': 'cross', 'isolatedMargin': '0.00000000', 'isAutoAddMargin': 'false', 'positionSide': 'LONG',
        'notional': '0', 'isolatedWallet': '0', 'updateTime': 0, 'isolated': False, 'adlQuantile': 0}
        """
        response = self.client.get_position_risk()
        print(response)

    def change_margin_type(self, symbol='BTCUSDT', marginType='ISOLATED'):
        """
        :param symbol:
        :param marginType: ISOLATED, CROSSED
        :return:
        """
        response = self.client.change_margin_type(symbol, marginType)
        print(response)

    def query_commission_rate(self, symbol='BTCUSDT'):
        """
        {'symbol': 'BTCUSDT', 'makerCommissionRate': '0.000200', 'takerCommissionRate': '0.000500'}
        """
        response = self.client.commission_rate(symbol)
        print(response)

    def query_trades(self, symbol='BTCUSDT'):
        response = self.client.get_account_trades(symbol)
        print(response)

    def query_income_history(self):
        response = self.client.get_income_history()
        print(response)

    def query_adl_quantile(self):
        response = self.client.adl_quantile()
        print(response)

    def query_force_orders(self):
        response = self.client.force_orders()
        print(response)


if __name__ == '__main__':
    u = UMFutureApi()
    u.connect()

    u.query_account_trades()

    # time.sleep(5)
    # u.send_order(symbol='BTCUSDT', order_price_type=OrderPriceType.FAK, offset_flag=OffsetFlag.OPEN,
    #                direction=Direction.LONG, volume=0.002, price=71000)
    #
    # time.sleep(5)
    # u.send_order(symbol='BTCUSDT', order_price_type=OrderPriceType.FAK, offset_flag=OffsetFlag.OPEN,
    #              direction=Direction.LONG, volume=0.002, price=71000)
    #
    # time.sleep(5)
    # u.send_order(symbol='BTCUSDT', order_price_type=OrderPriceType.FAK, offset_flag=OffsetFlag.CLOSE,
    #              direction=Direction.LONG, volume=0.002, price=70500)
    #
    # time.sleep(5)
    # u.send_order(symbol='BTCUSDT', order_price_type=OrderPriceType.FAK, offset_flag=OffsetFlag.CLOSE,
    #              direction=Direction.LONG, volume=0.002, price=70500)



    # time.sleep(5)
    # u.send_order(symbol='BTCUSDT', order_price_type=OrderPriceType.FAK, offset_flag=OffsetFlag.OPEN,
    #              direction=Direction.SHORT, volume=0.002, price=70500)
    #
    # time.sleep(5)
    # u.send_order(symbol='BTCUSDT', order_price_type=OrderPriceType.FAK, offset_flag=OffsetFlag.OPEN,
    #              direction=Direction.SHORT, volume=0.002, price=70500)
    #
    # time.sleep(5)
    # u.send_order(symbol='BTCUSDT', order_price_type=OrderPriceType.FAK, offset_flag=OffsetFlag.CLOSE,
    #              direction=Direction.SHORT, volume=0.002, price=71000)
    #
    # time.sleep(5)
    # u.send_order(symbol='BTCUSDT', order_price_type=OrderPriceType.FAK, offset_flag=OffsetFlag.CLOSE,
    #              direction=Direction.SHORT, volume=0.002, price=71000)

    while 1:
        pass

