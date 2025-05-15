

class OpenStrategy:
    def __init__(self, Backtestor):
        self.Backtestor = Backtestor

    def cal_singal(self,quote):
        last_price = float(quote.close)
        symbol = quote.symbol
        quote_time = quote.start_time

        self.trade_process.open(quote_time, symbol, 'LONG', last_price)

    @property
    def trade_process(self):
        return self.Backtestor.trade_process
