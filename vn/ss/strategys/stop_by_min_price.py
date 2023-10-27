import time

from a_songbo.vn.configs.vn_config import StopByMinPrice_params
from a_songbo.vn.enums.exchange_enum import OffsetFlag, ExchangeType, Direction, OrderPriceType
from a_songbo.vn.util.dingding import Dingding
from a_songbo.vn.util.sys_exception import common_exception


class StopByMinPrice:
    def __init__(self, gateway, portfilioprocess):
        self.gateway = gateway
        self.portfilioprocess = portfilioprocess
        self.variety_book = portfilioprocess.variety_book

        self.configs = StopByMinPrice_params

    def cal_signal(self, quote):
        instrument = quote['InstrumentID']
        now_timestamp = time.time()

        # 检查该合约是否在正在交易中
        if instrument in self.gateway.td_process.in_trading:
            return

        # 检查是否有持仓,有持仓才能平仓
        if instrument in self.gateway._instrument_positions:
            if 'SHORT' in self.gateway._instrument_positions[instrument]:
                position_data = self.gateway._instrument_positions[instrument]['SHORT']

                latest_price = round(float(quote['LastPrice']), 2)

                min_price_dict = self.gateway.min_price.get(instrument, 0)

                # 更新最小价格
                if not min_price_dict:
                    self.gateway.min_price[instrument] = {'price': latest_price, 'timestamp': now_timestamp}
                    return
                elif min_price_dict['price'] > latest_price:
                    self.gateway.min_price[instrument] = {'price': latest_price, 'timestamp': now_timestamp}
                    return
                elif position_data.open_avg < min_price_dict['price']:
                    self.gateway.min_price[instrument] = {'price': position_data.open_avg, 'timestamp': now_timestamp}
                    return

                min_price = min_price_dict['price']

                rise_rate = round(latest_price / min_price - 1, 6)

                close_flag = False
                # close_flag = True
                # print(instrument, rise_rate, position_data.open_avg, min_price, latest_price)
                # return

                # 盈利时
                if latest_price < position_data.open_avg and rise_rate > self.configs['profit_stop_rate']:
                    close_flag = 'profit_stop_rate'

                if latest_price > position_data.open_avg and rise_rate > self.configs['loss_stop_rate']:
                    close_flag = 'loss_stop_rate'

                if close_flag:
                    if int(position_data.yd):
                        offset_flag = OffsetFlag.CLOSE_YESTERDAY
                    else:
                        offset_flag = OffsetFlag.CLOSE_TODAY
                    direction = Direction.LONG
                    order_price_type = OrderPriceType.LIMIT
                    price = str(quote['LastPrice'])
                    # price = str(quote['AskPrice1'])
                    volume = str(self.configs['close_lot'])

                    # print('StopByMinPrice send:', close_flag, instrument, rise_rate,offset_flag, direction,
                    #       order_price_type, price, volume)

                    # Dingding.send_msg(f'StopByMinPrice 下单:   \n{close_flag} {instrument}  \n'
                    #                   f'offset_flag={offset_flag}  \ndirection={direction}  \n'
                    #                   f'order_price_type={order_price_type}  \n'
                    #                   f'price={price}  \nvolume={volume}')

                    self.gateway.logger.info(f'StopByMinPrice 下单:{instrument} {close_flag}'
                                             f'offset_flag={offset_flag} direction={direction} '
                                             f'order_price_type={order_price_type} '
                                             f'price={price} volume={volume}')

                    self.gateway.td_process.send_order(instrument, offset_flag, direction, order_price_type,
                                                       price, volume)
