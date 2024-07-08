import time

from a_songbo.vn.ss.strategy_gateway import StrategyGateway


ss_gateway = StrategyGateway()


def on_quote(quote):
    print(quote)


ss_gateway.ms_stub.subscribe_stream_in_new_thread(instruments=['rb2410'],
                                                               on_quote=on_quote)


while 1:
    time.sleep(30)

