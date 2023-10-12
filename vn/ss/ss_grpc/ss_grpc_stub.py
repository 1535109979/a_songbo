import grpc
from a_songbo.vn.proto import strategy_server_pb2_grpc, strategy_server_pb2, account_position_pb2


class StrategyGrpcStub:

    def __init__(self):
        channel = grpc.insecure_channel("127.0.0.1:9970")
        self.stub = strategy_server_pb2_grpc.StrategyStub(channel=channel)

    def get_stub(self):
        return self.stub


