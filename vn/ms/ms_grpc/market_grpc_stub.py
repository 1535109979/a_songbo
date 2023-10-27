
import grpc

from a_songbo.vn.proto import market_server_pb2,market_server_pb2_grpc
from a_songbo.vn.util.thread import run_in_new_thread


class VnMarketStub():
    def __init__(self):
        channel = grpc.insecure_channel("0.0.0.0:9950")
        self.sub = market_server_pb2_grpc.AsyncMarketServerStub(channel=channel)
        self.subscribed_instruments = set()
        self.sub_count = 0

    @run_in_new_thread(thread_name="MS")
    def subscribe_stream_in_new_thread(self, on_quote, instruments=None):
        self.subscribe_stream(on_quote=on_quote, instruments=instruments,)

    def subscribe_stream(self, on_quote, instruments=None):
        self.sub_count += len(instruments)
        print(self.sub_count, instruments)
        if instruments:
            self.subscribed_instruments.update(set(instruments))

        quote_reply_stream = self.sub.GetQuoteStream(market_server_pb2.Symbols(symbols=instruments))

        for i in quote_reply_stream:
            on_quote(i.quote)

    def add_subscribe(self, instruments):
        self.sub_count += len(instruments)
        print(self.sub_count, instruments)
        self.sub.AddSubscribe(market_server_pb2.Symbols(symbols=instruments))

    def stop_egine(self):
        print('market stub stop')
        self.sub.StopEngine(market_server_pb2.FlagReply(flag=True))


def on_quote(quote):
    print('get quote:', quote['InstrumentID'], quote)
    # print('get quote:', quote['InstrumentID'])


if __name__ == '__main__':
    VnMarketStub().subscribe_stream_in_new_thread(instruments=['lc2311', 'si2311'], on_quote=on_quote)
    # print('----')
    # VnMarketStub().add_subscribe(instruments=['rb2311', 'rb2311C4000'])
    # try:
    #     VnMarketStub().stop_egine()
    # except:
    #     pass
    while 1:
        pass

