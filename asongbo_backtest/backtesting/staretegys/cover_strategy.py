

class CoverStrategy:
    def __init__(self, Backtestor):
        self.Backtestor = Backtestor
        self.stop_profit_rate = Backtestor.instrument_config['stop_profit_rate']
        self.cover_multi_list = Backtestor.instrument_config['cover_multi_list']
        self.cover_decline_list = Backtestor.instrument_config['cover_decline_list']
        self.peak = Backtestor.instrument_config['peak']
        self.tough = Backtestor.instrument_config['tough']

    def cal_singal(self,quote):
        last_price = float(quote.close)
        symbol = quote.symbol
        quote_time = quote.start_time

        # tough_rise_rate = (last_price / self.position.tough - 1) * 100
        # peak_decline_rate = (1 - last_price / self.position.peak) * 100
        if not self.position:
            return

        if self.position.volume:
            if self.position.direction == 'LONG':
                decline_rate = (last_price / self.position.last_trade_price - 1) * 100
                profit_rate = (last_price / self.position.cost - 1) * 100

                if profit_rate > self.stop_profit_rate:
                    self.trade_process.stop_profit(quote_time, last_price, profit_rate / 100)
                    return

                if self.cover_count == len(self.cover_decline_list):
                    return

                if decline_rate < - self.cover_decline_list[self.cover_count] and self.cover_count < len(self.cover_decline_list):
                    self.trade_process.cover_order(quote_time, 'LONG', last_price, self.cover_multi_list[self.cover_count])

            if self.position.direction == 'SHORT':
                decline_rate = (1 - last_price / self.position.last_trade_price) * 100
                profit_rate = (1 - last_price / self.position.cost) * 100

                if profit_rate > self.stop_profit_rate and self.cover_count:
                    self.trade_process.stop_profit(quote_time, last_price, profit_rate / 100)
                    return

                if self.cover_count == len(self.cover_decline_list):
                    return

                if decline_rate < - self.cover_decline_list[self.cover_count]:
                    self.trade_process.cover_order(quote_time, 'SHORT', last_price, self.cover_multi_list[self.cover_count])

    @property
    def position(self):
        return self.Backtestor.position

    @property
    def trade_process(self):
        return self.Backtestor.trade_process

    @property
    def cover_count(self):
        return self.position.cover_count
