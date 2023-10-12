import asyncio

import grpc

from a_songbo.vn.proto import strategy_server_pb2_grpc, strategy_server_pb2, account_position_pb2


class StrategyGrpcServer(strategy_server_pb2_grpc.StrategyServicer):
    def __init__(self, gateway):
        # 策略函数封装
        self.gateway = gateway

    async def on_account_update(self, request: account_position_pb2.AccountBook, context):
        self.gateway.account_book = request
        print('on_account_update',len(self.gateway._instrument_positions),self.gateway._instrument_positions.keys())
        return strategy_server_pb2.FlagReply(flag=True)

    async def on_order_rtn(self, request: strategy_server_pb2.RtnRecord, context):
        """on_order_rtn
        {'volume': '100', 'volume_traded': '0', 'offset': 'OPEN', 'turnover': '0.0', 'exchange_type': 'SSE',
         'order_ref_id': '39240474845775827', 'price_type': 'LIMIT', 'limit_price': '15.88', 'status': 'ERROR',
         'account_id': '253191002712', 'order_id': '39240474845775827', 'update_time': '1692344097360077831',
         'instrument_category': 'STOCK', 'qty_left': '100', 'instrument': '600487', 'side': 'LONG',
         'error_msg': 'The price goes beyond the limit of rise and fall.', 'is_swap': '0', 'trading_day': '20230818',
         'insert_time': '1692344097360077831', 'order_status': '6', 'error_id': '11010122'}
        """
        rtn_dict = {k: v for k, v in request.rtn.items()}

        self.gateway.account_book = request.account_book
        return strategy_server_pb2.FlagReply(flag=True)

    async def on_trade_rtn(self, request: strategy_server_pb2.RtnRecord, context):
        """on_trade_rtn
        {'volume': '50', 'order_ref_id': '19280108191764', 'offset': 'CLOSE', 'turnover': '744.0',
         'id': '169234845893924047484577', 'exchange_type': 'SSE', 'trade_time': '1692348960604000', 'price': '14.88',
         'order_id': '39240474845776830', 'account_id': '253191002712', 'trade_id': '0000000000004589',
         'parent_order_id': '0141020000004421', 'instrument_category': 'STOCK', 'instrument': '600487', 'side': 'SHORT',
         'trading_day': '20230818'}
        """
        self.gateway.account_book = request.account_book

        rtn_dict = {k: v for k, v in request.rtn.items()}
        self.gateway.on_trade_rtn(rtn_dict)

        return strategy_server_pb2.FlagReply(flag=True)

    async def run(self):
        g = grpc.aio.server()
        g.add_insecure_port("0.0.0.0:9970")
        strategy_server_pb2_grpc.add_StrategyServicer_to_server(self, g)
        await g.start()
        await g.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(StrategyGrpcServer(None).run())
