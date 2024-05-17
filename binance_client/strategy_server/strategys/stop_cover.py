from a_songbo.binance_client.trade.do.position import InstrumentPosition
from a_songbo.binance_client.utils.exchange_enum import Direction, OffsetFlag, OrderPriceType


class StopLoss:
    def __init__(self, gateway):
        self.gateway = gateway
        self.td_gateway = gateway.td_gateway
        self.stop_loss_rate = 0.05
        self.cover_rate = 0.005
        self.can_cover = self.gateway.can_cover

    def cal_indicator(self, quote):
        pass

    def cal_singal(self, quote):
        last_price = float(quote['last_price'])
        instrument = quote['symbol']

        long_position: InstrumentPosition = self.td_gateway.account_book.get_instrument_position(
            f'{instrument}.{self.td_gateway.exchange_type}', Direction.LONG)

        short_position: InstrumentPosition = self.td_gateway.account_book.get_instrument_position(
            f'{instrument}.{self.td_gateway.exchange_type}', Direction.SHORT)

        if long_position.cost:
            fall_rate = last_price / long_position.cost - 1
            if fall_rate < - self.cover_rate and self.can_cover:
                self.td_gateway.insert_order(instrument, OffsetFlag.OPEN, Direction.LONG,
                                             OrderPriceType.LIMIT, str(float(last_price)), long_position.volume)
                self.can_cover = False

            elif fall_rate < -self.stop_loss_rate:
                self.td_gateway.insert_order(instrument, OffsetFlag.CLOSE, Direction.LONG,
                                             OrderPriceType.LIMIT, str(float(last_price)), long_position.volume)

                self.gateway.stop_loss_flag = True
                self.gateway.logger.info(f'stop_loss=LONG')

        if short_position.cost:
            fall_rate = 1 - last_price / short_position.cost
            if fall_rate < - self.cover_rate and self.can_cover:
                self.td_gateway.insert_order(instrument, OffsetFlag.OPEN, Direction.SHORT,
                                             OrderPriceType.LIMIT, str(float(last_price)), short_position.volume)
                self.can_cover = False
                self.gateway.logger.info(f'cover short: l={last_price} cost={short_position.cost} '
                                         f'v={short_position.volume}')
            if fall_rate < -self.stop_loss_rate:
                self.td_gateway.insert_order(instrument, OffsetFlag.CLOSE, Direction.SHORT,
                                             OrderPriceType.LIMIT, str(float(last_price)), short_position.volume)
                self.gateway.stop_loss_flag = True
                self.gateway.logger.info(f'stop_loss=short')
