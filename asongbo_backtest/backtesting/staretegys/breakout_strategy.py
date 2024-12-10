

class BreakoutStrategy:
    def __init__(self, Backtestor):
        self.Backtestor = Backtestor
        self.windows = Backtestor.instrument_config['windows']
        self.roll_mean_period = Backtestor.instrument_config['roll_mean_period']
        self.interval_period = Backtestor.instrument_config['interval_period']
        self.open_direction = Backtestor.instrument_config['open_direction']
        self.min_save_window = max(self.windows, self.interval_period * 2 + self.roll_mean_period)

        self.am = []
        self.roll_mean_list = []

    def cal_singal(self,quote):
        last_price = float(quote.close)
        symbol = quote.symbol
        quote_time = quote.start_time

        self.regressio_flag = None
        self.trend_flag = None

        if len(self.am) < self.min_save_window:
            self.am.append(last_price)
            if len(self.am) >= self.roll_mean_period:
                roll_mean = round(sum([float(x) for x in self.am[-self.roll_mean_period:]]) / self.roll_mean_period, 8)
                self.roll_mean_list.append(roll_mean)

            return

        self.am = self.am[-self.min_save_window:]
        self.last_n_max = max(self.am[-self.windows:])
        self.last_n_min = min(self.am[-self.windows:])
        self.min_dr = last_price / self.last_n_min - 1
        self.max_dr = last_price / self.last_n_max - 1

        self.am.append(last_price)
        roll_mean = round(sum([float(x) for x in self.am[-self.roll_mean_period:]]) / self.roll_mean_period, 8)
        self.roll_mean_list.append(roll_mean)
        self.roll_mean_list = self.roll_mean_list[-self.min_save_window * 2:]

        if last_price < self.last_n_min:
            self.regressio_flag = 'LONG'
        elif last_price > self.last_n_max:
            self.regressio_flag = 'SHORT'

        if last_price > self.roll_mean_list[-self.interval_period] > self.roll_mean_list[-self.interval_period * 2]:
            self.trend_flag = 'SHORT'
        elif last_price < self.roll_mean_list[-self.interval_period] < self.roll_mean_list[-self.interval_period * 2]:
            self.trend_flag = 'LONG'

        if self.regressio_flag:
            if self.regressio_flag != self.trend_flag:
                self.trade_process.reverse(quote_time, symbol, self.regressio_flag,last_price)

    @property
    def trade_process(self):
        return self.Backtestor.trade_process
