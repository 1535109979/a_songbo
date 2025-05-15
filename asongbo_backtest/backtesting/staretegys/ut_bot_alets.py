import pandas as pd
import numpy as np

class UtBotAletStrategy:
    def __init__(self, Backtestor):
        self.Backtestor = Backtestor
        self.atr_period = 10
        self.keyvalue = 1
        self.exit_signal_deviation = 0.05

        self.am = []

    def cal_singal(self,quote):
        last_price = float(quote.close)
        symbol = quote.symbol
        quote_time = quote.start_time

        self.am.append(last_price)
        if len(self.am) < self.atr_period + 2:
            return
        # self.am.pop(0)

        df = pd.DataFrame(self.am, columns=['close'])
        df_res = self.cal_ut_bot_alerts(df)
        signal = df_res.loc[len(df_res)-1]['signal']
        if signal == 1:
            print(signal)
        if signal == -1:
            print(signal)


    def cal_ut_bot_alerts(self, df):
        df['atr'] = df['close'].rolling(window=self.atr_period).std() * np.sqrt(self.atr_period)
        df['ema_short'] = df['close'].ewm(span=1, adjust=False).mean()
        df['linear_regression'] = df['close'].rolling(window=self.atr_period).mean()
        df['exit_level'] = df['linear_regression'] * (1 + self.exit_signal_deviation)

        df['signal'] = 0
        df.loc[df['close'] > df['ema_short'] + self.keyvalue * df['atr'], 'signal'] = 1  # Buy signal
        df.loc[df['close'] < df['ema_short'] - self.keyvalue * df['atr'], 'signal'] = -1  # Sell signal

        return df
