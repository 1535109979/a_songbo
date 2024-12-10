import sqlite3

import pandas
import pandas as pd
import warnings

from matplotlib import pyplot as plt

from a_songbo.vedio_study.协程.协程汇总 import main2

warnings.filterwarnings("ignore")
pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)

class AnaHourdata:
    def __init__(self):

        with sqlite3.connect('binance_quote_data.db') as conn:
            self.df_hour = pd.read_sql(f'select * from hour_data ', conn)

    def cal_ind(self):
        def process_symbol(df_symbol):
            df_symbol = df_symbol.sort_values(by=['hour'],ascending=True).reset_index(drop=True)
            df_symbol['index'] = df_symbol.index
            df_symbol['day'] = df_symbol['hour'].apply(lambda x: x[:-3])
            daily_max = df_symbol.groupby('day').apply(lambda x: x['min_max_rate'].sum()).max()

            max_change = df_symbol['min_max_rate'].max()
            std = df_symbol['min_max_rate'].std()
            mean = df_symbol['min_max_rate'].mean()

            r_10 = abs(df_symbol['index'].tail(240).corr(df_symbol['close'].tail(240)))
            r_30 = abs(df_symbol['index'].tail(240 * 3).corr(df_symbol['close'].tail(240 * 3)))
            return float(max_change), std, mean, r_10, r_30, daily_max

        df_res = self.df_hour.groupby('symbol').apply(process_symbol)
        df_res = df_res.reset_index()
        df_res.columns =['symbol', 'data']

        df_res[['max_change','std', 'mean', 'r_10', 'r_30','daily_max']] = df_res['data'].apply(pd.Series)
        print(df_res)
        df_res = df_res[df_res['max_change'] < 20]
        df_res = df_res.sort_values(by=['r_10'], ascending=False)
        df_res.to_csv('res.csv')
        # print(df_res)

    def plot_symbol(self):
        d = self.df_hour[self.df_hour['symbol'] == 'gmxusdt']
        plt.plot(d['min_max_rate'])
        plt.title('Boxplot of Data')
        plt.show()


if __name__ == '__main__':
    AnaHourdata().cal_ind()
    # AnaHourdata().plot_symbol()

