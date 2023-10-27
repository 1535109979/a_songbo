import grpc

from byt_trading_proto.src.protos import trade_server_pb2_grpc, trade_server_pb2

channel = grpc.insecure_channel("127.0.0.1:9920")
ts_stub = trade_server_pb2_grpc.TradeStub(channel=channel)

instrument = "600487"
price = 13

order_id = ts_stub.insert_order(trade_server_pb2.InsertOrderRequest(
    account_id='253191002712', instrument=instrument,
    exchange_type="SSE", source_type="CTP",
    # offset_flag="OPEN",
    offset_flag="CLOSE",
    direction="LONG", order_price_type="LIMIT",
    price=str(price), volume=str(100)))
print(">>> order_id:", order_id)

# res = ts_stub.cancel_order(
#     trade_server_pb2.CancelOrderRequest(
#         order_id='39240474845781857',
#         account_id='253191002712'
#     )
# )
# print(">>> cancel_order:", res)


