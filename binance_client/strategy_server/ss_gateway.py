from concurrent.futures import ThreadPoolExecutor

from a_songbo.binance_client.market.md_gateway import BiFutureMdGateway
from a_songbo.binance_client.strategy_server.strategys.breakout import BreakoutStrategy
from a_songbo.binance_client.strategy_server.strategys.stop_cover import StopLoss
from a_songbo.binance_client.trade.td_gateway import BiFutureTdGateway
from a_songbo.binance_client.utils.thread import submit


class BiFutureSsGateway:
    def __init__(self):
        self.ms_gateway = BiFutureMdGateway()
        self.ms_thread_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ms")

        self.td_gateway = BiFutureTdGateway()
        self.td_gateway.connect()
        self.logger = self.td_gateway.logger
        self.can_cover = True

        self.stop_loss_flag = None
        self.strategy_list = []
        self.load_strategy()

    def load_strategy(self):
        self.strategy_list.append(BreakoutStrategy(self))
        self.strategy_list.append(StopLoss(self))

    def start(self):
        submit(_executor=self.ms_thread_pool, _fn=self.ms_gateway.subscribe,
               _kwargs=dict(instrument=['EOSUSDT'], on_quote=self.on_quote))

        # self.ms_gateway.subscribe(['EOSUSDT'], on_quote=self.on_quote)
        print('---')

    def on_quote(self, quote):
        for strategy in self.strategy_list:
            strategy.cal_indicator(quote)

        for strategy in self.strategy_list:
            strategy.cal_singal(quote)


if __name__ == '__main__':
    BiFutureSsGateway().start()

    while 1:
        pass

