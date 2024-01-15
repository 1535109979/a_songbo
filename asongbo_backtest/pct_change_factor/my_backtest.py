import sqlite3
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt
import pandas as pd

import warnings
warnings.filterwarnings('ignore')


class MyBacktest:
    def __init__(self, df, interval=10, pct_change_periods=120):
        self.df = df
        self.interval = interval
        self.pct_change_periods = pct_change_periods

        self.top_returns = None
        self.print_data = False
        self.close_position_times = 0

        self.position = None
        self.account_value = 1
        self.account_value_list = [1]

        self.cal_daily_top_returns()
        self.run_backtest()

    def cal_daily_top_returns(self):
        self.df['return'] = self.df.groupby('variety')['close_price'].pct_change(periods=self.pct_change_periods)
        self.df['interest_22mean'] = self.df.groupby('variety')['open_interest'].transform(lambda x: x.rolling(22).mean())
        self.df = self.df[self.df['date'] > '2015-01-01']
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['next_22_price'] = self.df['close_price'].shift(-self.interval)
        self.df = self.df.dropna()

        def get_data(df_date):
            df_date = df_date[df_date['interest_22mean'] > 100000]
            return df_date.nlargest(5, 'return')

        self.top_returns = self.df.groupby('date').apply(get_data).reset_index(drop=True).sort_values(by='date')

    def run_backtest(self):
        all_date = list(set(self.top_returns['date'].tolist()))
        all_date.sort()

        interval = self.interval
        index = interval
        change_position_date = all_date[index]

        for date in all_date[:-interval]:
            df_date = self.top_returns[self.top_returns['date'] == date][['date', 'close_price', 'variety_name']]
            varietys = df_date.set_index('variety_name')['close_price'].to_dict()

            if not self.position:
                self.position = varietys
                if self.print_data:
                    print(date, 'position', self.position)
            else:
                if date == change_position_date:
                    if self.print_data:
                        print('--------', date, '进入换仓日,净值', self.account_value, '--------')

                    if len(df_date) < 5:
                        index += 1
                        change_position_date = all_date[index]
                        continue

                    index += interval
                    change_position_date = all_date[index]
                    # print(change_position_date)

                    new_account_value = 0

                    position_copy = self.position.copy()
                    for k, v in position_copy.items():
                        if k not in varietys:
                            result = self.df.query('date<=@date and variety_name==@k')['close_price'].values[-1]
                            new_account_value += self.account_value * 0.2 * (v / result) * (1 - 0.001)
                            self.close_position_times += 1
                            if self.print_data:
                                print('del:', k, v, result, v / result)
                            self.position.pop(k)
                        else:
                            new_account_value += self.account_value * 0.2
                    self.account_value = new_account_value
                    self.account_value_list.append(self.account_value)

                    for k, v in varietys.items():
                        if k not in self.position:
                            if self.print_data:
                                print('add:', k)
                            self.position[k] = v

                    if self.print_data:
                        print(date, 'position', self.position)
                        print(date, '净值', self.account_value)


def read_data():
    with sqlite3.connect('../database/future_data.db') as conn:
        df = pd.read_sql('select * from future_daily_data', conn)

    df = df.sort_values(by='date')
    return df


def run_backtest(df, i, j):
    try:
        mb = MyBacktest(df, i, j)
        print(i, j, mb.account_value)
        # with open('result/values_result.csv','a')as f:
        #     f.write(f'{i}, {j}, {mb.account_value}\n')
    except:
        print('error', i, j)


if __name__ == '__main__':
    df = read_data()

    with ProcessPoolExecutor(max_workers=10) as executor:
        for i in range(4, 50, 2):
            for j in range(40, 300, 20):
                executor.submit(run_backtest, df, i, j)
