import time
from dataclasses import dataclass
from collections import defaultdict

from a_songbo.vn.enums.exchange_enum import OffsetFlag, ExchangeType, Direction, OrderPriceType
from a_songbo.vn.ts.ts_grpc.trade_grpc_stub import TradeGrpcStub
from a_songbo.vn.util.dingding import Dingding
from a_songbo.vn.util.lock import instance_synchronized
from a_songbo.vn.util.sys_exception import common_exception


class TradeProcess:
    def __init__(self, gateway):
        self.gateway = gateway
        self.td_stub = TradeGrpcStub(gateway)
        # 记录交易中的订单
        self.in_trading = dict()

    @common_exception(log_flag=True)
    @instance_synchronized
    def send_order(self, instrument, offset_flag: OffsetFlag,
                   direction: Direction, order_price_type: OrderPriceType, price: str, volume: str, exchange_type=None):
        if not exchange_type:
            exchange_type = ExchangeType.get_by_value(self.gateway.left_day_map[instrument]['exchange'])

        self.gateway.logger.info(f'<trade_process send_order> instrument={instrument} exchange_type={exchange_type} '
                                 f'offset_flag={offset_flag} direction={direction} order_price_type={order_price_type} '
                                 f'order_price_type={order_price_type} price={price} volume={volume}')
        order_id = self.td_stub.insert_order(instrument, exchange_type, offset_flag, direction, order_price_type, price, volume)
        # Dingding.send_msg(f'下单成功  \ninstrument:{instrument}  \norder_id:{order_id.order_id}')
        self.gateway.logger.info(f'下单成功 instrument:{instrument} order_id:{order_id.order_id}')
        self.in_trading[instrument] = TradingOrder.create_by_order_data(instrument, exchange_type, offset_flag,
                                                                        direction, order_price_type, price, volume)

    @common_exception(log_flag=True)
    @instance_synchronized
    def updata_by_trade_rtn(self, data):
        self.gateway.logger.info(f'<updata_by_trade_rtn> data={data}')

        trade_order = self.in_trading.get(data['instrument'])
        if trade_order:
            trade_order.update_by_trade_rtn(data)
            if trade_order.left == 0:
                self.in_trading.pop(data['instrument'])
                # print(data['instrument'], '全部成交', 'now positions', self.gateway._instrument_positions.keys(),
                #       'in_trading:', self.in_trading.keys())

                Dingding.send_msg(f'{data["instrument"]} 全部成交   \n'
                                  f'当前持仓数量：{len(self.gateway._instrument_positions)}  \n' +
                                  self.gateway.create_position_msg())
                # 平仓后清除最小价
                if (trade_order.offset_flag == OffsetFlag.CLOSE_TODAY or
                        trade_order.offset_flag == OffsetFlag.CLOSE_YESTERDAY):
                    self.gateway.min_price.pop(data['instrument'])
                    Dingding.send_msg(f'当前记录 {len(self.gateway.min_price)} 条min_price:' +
                                      ','.join(self.gateway.min_price.keys()))


@dataclass
class TradingOrder:
    instrument: str
    exchange_type: str
    offset_flag: str
    direction: str
    order_price_type: str
    price: str
    volume: str
    insert_time: float
    left: int = 0

    @classmethod
    def create_by_order_data(cls, instrument, exchange_type, offset_flag, direction, order_price_type, price, volume):
        return cls(instrument=instrument, exchange_type=exchange_type, offset_flag=offset_flag, direction=direction,
                   order_price_type=order_price_type, price=price, volume=volume, left=int(volume),
                   insert_time=time.time())

    def update_by_trade_rtn(self, data):
        self.left -= int(data['volume'])


