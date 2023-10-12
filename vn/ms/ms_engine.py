import asyncio
from asyncio import events

from a_songbo.vn.ms.ms_grpc.market_grpc_server import MarkerGrpcServer
from a_songbo.vn.ms.vn_market_gateway import VnMarketGateway


class MarketEngine:

    def __init__(self):
        self.gateway = VnMarketGateway()

    def start(self):
        self.gateway.loop.run_until_complete(MarkerGrpcServer(self.gateway).run())


if __name__ == '__main__':
    MarketEngine().start()
