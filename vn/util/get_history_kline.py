import pandas
from tqsdk import TqApi, TqAuth, tafunc

pandas.set_option("expand_frame_repr", False)
# pandas.set_option("display.max_rows", 2000)


class TianQing:
    def __init__(self):
        self.api = TqApi(auth=TqAuth("15605173271", "songbo1997"))
        self.klines_dict = dict()

    def get_data(self, symbol: str):
        klines = self.api.get_kline_serial(symbol, 86400)
        klines.datetime = klines.datetime.map(tafunc.time_to_datetime)
        print(klines)

    def get_klines(self, symbols: list):
        for symbol in symbols:
            self.get_data(symbol)
        self.api.close()


if __name__ == '__main__':
    symbols = ["SHFE.rb2311C4100"]
    TianQing().get_klines(symbols)

