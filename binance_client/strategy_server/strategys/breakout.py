from a_songbo.binance_client.trade.do.position import InstrumentPosition
from a_songbo.binance_client.utils.exchange_enum import Direction, OffsetFlag, OrderPriceType


class BreakoutStrategy:
    def __init__(self, gateway):
        self.gateway = gateway
        self.td_gateway = gateway.td_gateway
        self.open_direction = Direction.LONG
        self.windows = 5
        self.open_volume = 10

        self.am = []
        self.last_n_min = self.last_n_max = None
        self.trading_info = None

    def cal_indicator(self, quote):
        if not quote.get('is_closed', 0):
            return

        last_price = quote['last_price']

        if len(self.am) < self.windows:
            self.am.append(last_price)
            return

        self.am = self.am[-self.windows:]
        self.last_n_max = max(self.am)
        self.last_n_min = min(self.am)

        self.am.append(last_price)

    def cal_singal(self, quote):
        if not len(self.td_gateway.open_orders_map):
            self.trading_info = None

        if not quote.get('is_closed', 0):
            return

        last_price = quote['last_price']
        instrument = quote['symbol']

        if not self.last_n_min:
            return

        # 开仓方向
        open_direction = None
        if last_price < self.last_n_min:
            open_direction = self.open_direction
        elif last_price > self.last_n_max:
            open_direction = self.open_direction.get_opposite_direction()

        self.gateway.logger.info(f"<cal_singal>w={self.windows} l={last_price} min={self.last_n_min} "
                                 f"max={self.last_n_max} open_direction={open_direction}")

        if not open_direction:
            return

        direction_position: InstrumentPosition = self.td_gateway.account_book.get_instrument_position(
            f'{instrument}.{self.td_gateway.exchange_type}', open_direction)
        opposite_direction_position: InstrumentPosition = self.td_gateway.account_book.get_instrument_position(
            f'{instrument}.{self.td_gateway.exchange_type}', open_direction.get_opposite_direction())

        self.gateway.logger.info(f'direction_position={direction_position}')
        self.gateway.logger.info(f'opposite_direction_position={opposite_direction_position}')

        if direction_position.volume:
            return
        else:
            if len(self.td_gateway.open_orders_map):
                if (self.trading_info and open_direction == self.trading_info[0]
                        and last_price == self.trading_info[1]):
                    return
                self.td_gateway.cancel_cancel_all_order(instrument)

            self.td_gateway.insert_order(instrument, OffsetFlag.OPEN, open_direction,
                                         OrderPriceType.LIMIT, str(float(last_price)), self.open_volume)

            if opposite_direction_position.volume:
                self.td_gateway.insert_order(instrument, OffsetFlag.CLOSE, open_direction.get_opposite_direction(),
                                             OrderPriceType.LIMIT, str(float(last_price)), self.open_volume)

            self.trading_info = (open_direction, last_price)

