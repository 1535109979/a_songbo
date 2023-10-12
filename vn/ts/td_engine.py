import asyncio

from a_songbo.vn.ts.ts_grpc.trade_grpc_server import TradeGrpcServer
from a_songbo.vn.ts.vn_trade_gateway import VnTdGateway
from a_songbo.vn.util.dingding import Dingding


class TdEngine:

    def __init__(self):
        self.gateway = VnTdGateway()

    def start(self):
        self.gateway.client.connect()

        # if not self.gateway.client.ready:
        #     Dingding.send_msg('交易服务启动失败')

        asyncio.run(TradeGrpcServer(self.gateway).run())


if __name__ == '__main__':
    TdEngine().start()


