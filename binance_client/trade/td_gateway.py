import logging
import time

from a_songbo.binance_client.trade.future_api import BiFutureTd
from a_songbo.binance_client.unit_test.sys_demo import divs
from a_songbo.binance_client.utils.exchange_enum import OffsetFlag, Direction, OrderPriceType, ExchangeType


class BiFutureTdGateway:
    def __init__(self):
        self.create_logger()
        self.client = BiFutureTd(self)
        self.account_book = self.client.account_book
        self.open_orders_map = []

    def connect(self):
        self.client.connect()

    def insert_order(self, instrument: str, offset_flag: OffsetFlag, direction: Direction,
                      order_price_type: OrderPriceType, price: float, volume: float,
                      cancel_delay_seconds: int = 0, **kwargs) -> str:
        """ 向交易所报单
        做多开仓=OPEN:LONG    做空开仓=OPEN:SHORT
        做多平仓=CLOSE:LONG   做空平仓=CLOSE:SHORT
        """
        client_order_id = self.client.insert_order(
            instrument=instrument, offset_flag=offset_flag, direction=direction,
            order_price_type=order_price_type, price=price, volume=volume,
            cancel_delay_seconds=cancel_delay_seconds, **kwargs)

        self.open_orders_map.append(client_order_id)

        return client_order_id

    def on_order(self, rtn_order):

        if (len(self.open_orders_map) and rtn_order.order_id in self.open_orders_map
                and rtn_order.order_status.is_completed()):
            self.open_orders_map.remove(rtn_order.order_id)
            self.logger.info(f'open_orders_map: {self.open_orders_map}')

    def cancel_cancel_all_order(self, instrument):
        self.client.cancel_all_order(instrument)

    def get_api_configs(self):
        return {
            'stream_url': 'wss://fstream.binance.com',
            'base_url': 'https://fapi.binance.com',
            # 'api_key': '8kHJ8xMwb8wZkrTy17IVOym4CDo5qS6JFP8suvpsDaWCqjuBuIAn29HFYKuQM1bE',
            # 'secret_key': 'uUH1X2sz5jnMVhL44zxHiphnxhoQ5swPs62gFg4JFLCRayWwFr2MZJm9dJlaM2WK',
            'api_key': 'lfFQPMO2aNVuq6RI8h4PzPObfLQjWsvPcJ8zpfbYb0TJZV3zFmuxTTN7z0aj7lnc',
            'secret_key': '9x0h75LjgFw7QwAa7yYFOvDOpN4VKPx4i6iRiicTadZpTLMrTqW4uetm1GSg8srk',
            }

    def send_position_error_msg(self, instrument, error):
        self.logger.error(f"<send_position_error_msg> {instrument} {error}")

    def send_start_unsuccessful_msg(self, msg):
        self.logger.error(f"<send_start_unsuccessful_msg> {msg}")

    def send_start_msg(self, login_reqid):
        self.logger.info(f"<send_start_msg> {login_reqid}")

    def on_account_update(self):
        self.logger.info(f"<on_account_update>")

    def gen_error_order_id(self, err_msg):
        print(err_msg)

    def create_logger(self):
        self.logger = logging.getLogger('bi_future_ts')
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('/Users/edy/byt_pub/a_songbo/binance_client/logs/bi_future_ts.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    @property
    def exchange_type(self):
        return ExchangeType.BINANCE_F


if __name__ == '__main__':
    td = BiFutureTdGateway()
    td.connect()

    time.sleep(5)
    # posi = td.account_book.get_instrument_position(f'EOSUSDT.{td.exchange_type}', Direction.LONG)
    # print(posi)

    td.insert_order('EOSUSDT', OffsetFlag.OPEN, Direction.LONG,
                    OrderPriceType.LIMIT, 0.79, 10)

    while 1:
        pass
