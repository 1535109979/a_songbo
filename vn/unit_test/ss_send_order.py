from a_songbo.vn.ss.strategy_gateway import StrategyGateway
from a_songbo.vn.ts.vn_trade_gateway import VnTdGateway
from a_songbo.vn.enums.exchange_enum import OffsetFlag, ExchangeType, Direction, OrderPriceType


class StrategyGatewaytest:
    def __init__(self):
        self.gateway = StrategyGateway()

    def send_order(self):
        instrument = 'rb2410'
        offset_flag = OffsetFlag.OPEN
        direction = Direction.LONG
        order_price_type = OrderPriceType.LIMIT
        price = str(3660)
        volume = str(1)

        self.gateway.td_process.send_order(instrument, offset_flag, direction, order_price_type,
                                           price, volume)


if __name__ == '__main__':
    StrategyGatewaytest().send_order()

    while 1:
        pass