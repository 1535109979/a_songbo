import grpc

from a_songbo.vn.enums.exchange_enum import Direction
from a_songbo.vn.proto import trade_server_pb2_grpc, trade_server_pb2
from a_songbo.vn.util import type_util
from a_songbo.vn.util.api_enum import ResultCodeMsg


class TradeGrpcServer(trade_server_pb2_grpc.TradeServicer):
    def __init__(self, gateway):
        self.gateway = gateway
        self.logger = self.gateway.logger

    async def _check_request(self, request, context):
        if not self.gateway.client.ready:
            return await context.abort(
                code=grpc.StatusCode.UNAVAILABLE, details="当前服务状态不能发起请求")

    async def sub_account(self, request: trade_server_pb2.SubAccountRequest, context):
        """ 交易服务实际已订阅账号，返回账号信息以表示账号订阅成功 """
        # abort = await self._check_request(request=request, context=context)
        # if abort:
        #     return abort
        try:
            return self.gateway.create_account_book_mo(need_instrument_books=True)
        except Exception as e:
            self.logger.exception("!!!sub_account error= %s !!! request = %s", e, request)
            return await context.abort(code=grpc.StatusCode.UNAVAILABLE, details=str(e))

    async def insert_order(self, request: trade_server_pb2.InsertOrderRequest, context):
        """ 报单 """
        # abort = await self._check_request(request=request, context=context)
        # if abort:
        #     return abort
        try:
            price: float = type_util.get_precision_number(
                request.price, precision=2)

            volume = type_util.convert_to_int(request.volume)
            if not volume or not price:
                self.logger.error(
                    f"!!! Cannot insert_order !!! {request.account_id} "
                    f"{request.instrument} {request.exchange_type} {request.source_type} "
                    f"{request.offset_flag} {request.direction} {request.order_price_type} "
                    f"price={price} volume={volume}")
                self.gateway.send_msg()
                error_type = ResultCodeMsg.INCORRECT_PARAS
                return trade_server_pb2.InsertOrderReply(
                    error_code=str(error_type.get_code()),
                    error_msg=error_type.get_format_msg(f"volume={volume},price={price}"))

            self.logger.info("<%s> account_id=%s %s %s %s %s %s %s price=%s volume=%s",
                             context.peer(), request.account_id, request.instrument,
                             request.exchange_type, request.source_type,
                             request.offset_flag, request.direction,
                             request.order_price_type, price, volume)
            order_id: str = self.gateway.insert_order(
                instrument=request.instrument, exchange_type=request.exchange_type,
                offset_flag=request.offset_flag, direction=Direction.get_by_value(request.direction),
                order_price_type=request.order_price_type, price=price, volume=volume)
            if order_id and str(order_id) != "0":
                return trade_server_pb2.InsertOrderReply(order_id=str(order_id))
            else:
                error_type = ResultCodeMsg.EXCHANGE_EXCEPTION
                return trade_server_pb2.InsertOrderReply(
                    error_code=str(error_type.get_code()),
                    error_msg=error_type.get_format_msg(f"order_id={order_id}"))
        except Exception as e:
            e_str = str(e)
            print(e_str)

    async def run(self):
        g = grpc.aio.server()
        g.add_insecure_port("0.0.0.0:9960")
        trade_server_pb2_grpc.add_TradeServicer_to_server(self, g)
        await g.start()
        await g.wait_for_termination()

