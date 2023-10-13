import re
import time

from a_songbo.vn.configs.vn_config import SellStrategy_params
from a_songbo.vn.enums.exchange_enum import OffsetFlag, ExchangeType, Direction, OrderPriceType
from a_songbo.vn.util.dingding import Dingding


class SellStrategy:
    def __init__(self, gateway, portfilioprocess):
        self.gateway = gateway
        self.portfilioprocess = portfilioprocess
        self.variety_book = portfilioprocess.variety_book

        self.configs = SellStrategy_params

    def cal_signal(self, quote):
        instrument = quote['InstrumentID']
        last_price = round(float(quote['LastPrice']), 2)

        variety = re.match(r'.+[A-Z]', instrument).group()
        now_timestamp = time.time()

        # 检查是否有持仓
        for code in self.gateway._instrument_positions.keys():
            if variety in code:
                return

        # 检查该合约是否在正在交易中
        for code in self.gateway.td_process.in_trading.keys():
            if variety in code:
                return

        # 当前价格小于半小时前
        saved_price = self.gateway.saved_price.get(instrument, 0)
        if not saved_price:
            return
        if not last_price < saved_price['price']:
            return

        # 当前隐含波动率
        imp_timestamp = self.gateway.last_imp.get(instrument, 0)
        if not imp_timestamp:
            return
        imp = imp_timestamp['imp']

        # # 隐含波动率上一次存储值
        # save_imp_value = self.gateway.saved_imp.get(instrument, 0)
        # if not save_imp_value:
        #     self.gateway.saved_imp[instrument] = {'imp': imp, 'timestamp': now_timestamp}
        #     return

        # if self.configs['sell_imp_limit'] <= imp < save_imp_value['imp']:
        if self.configs['sell_imp_limit'] <= imp:
            offset_flag = OffsetFlag.OPEN
            direction = Direction.SHORT
            order_price_type = OrderPriceType.LIMIT
            price = str(last_price)
            # price = str(quote['BidPrice1'])
            volume = str(self.configs['sell_lot'])

            # print('SellStrategy send order:', instrument, imp,offset_flag, direction, order_price_type,
            #                                price, volume)

            # Dingding.send_msg(f'SellStrategy 下单:   \n {instrument}  \n'
            #                   f'offset_flag={offset_flag}  \ndirection={direction}  \n'
            #                   f'order_price_type={order_price_type}  \n'
            #                   f'price={price}  \nvolume={volume}')

            self.gateway.logger.info(f'SellStrategy 下单:{instrument} '
                                     f'offset_flag={offset_flag} direction={direction} '
                                     f'order_price_type={order_price_type} '
                                     f'price={price} volume={volume}')
            self.gateway.td_process.send_order(instrument, offset_flag, direction, order_price_type,
                                           price, volume)

