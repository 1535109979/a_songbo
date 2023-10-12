import grpc

from a_songbo.vn.enums.exchange_enum import Direction, OffsetFlag, ExchangeType, OrderPriceType
from a_songbo.vn.proto import trade_server_pb2_grpc, trade_server_pb2


class TradeGrpcStub():
    def __init__(self, gateway):
        channel = grpc.insecure_channel("127.0.0.1:9960")
        self.stub = trade_server_pb2_grpc.TradeStub(channel=channel)
        self.gateway = gateway

    def insert_order(self, instrument, exchange_type: ExchangeType, offset_flag: OffsetFlag,
                     direction: Direction, order_price_type: OrderPriceType, price: str, volume: str):

        # print(exchange_type.value,offset_flag.value,direction.value,order_price_type.value)

        order_id = self.stub.insert_order(trade_server_pb2.InsertOrderRequest(
            account_id='210380', instrument=instrument, exchange_type=exchange_type.value,
            source_type="CTP", offset_flag=offset_flag.value,
            direction=str(direction.value), order_price_type=order_price_type.value,
            price=str(price), volume=volume))

        return order_id

    def sub_account(self, account_id: str = ''):
        try:
            response = self.stub.sub_account(trade_server_pb2.SubAccountRequest(
                account_id=account_id))
            self.gateway.account_book = response
            return True
        except:
            self.gateway.send_msg('!!! error !!! 策略服务启动失败  \nsub_account error', isatall=True)

    def get_stub(self):
        return self.stub


if __name__ == '__main__':
    TradeGrpcStub(None).insert_order()
    # TradeGrpcStub().sub_account()


