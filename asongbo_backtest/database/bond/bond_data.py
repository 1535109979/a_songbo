import sqlite3
from datetime import datetime

import akshare as ak
import pandas
import pandas as pd

pandas.set_option("expand_frame_repr", False)


class BondData:

    def process(self):
        df = self.read_data('all_bond_data')
        codes = df['债券代码'].tolist()
        for code in codes:
            try:
                self.get_premium(code)
            except:
                continue

    def save_bond_daily_data(self):
        df = self.read_data('all_bond_data')
        exist_code = self.read_data('bond_daily_data')['code'].drop_duplicates().tolist()

        codes = df['债券代码'].tolist()
        for code in codes:
            if code in exist_code:
                continue
            try:
                self.get_daily_data(code)
            except:
                print(f'error code {code}')

    def get_all_bond(self):
        # 获取所有可转债
        df = ak.bond_zh_cov()
        self.save_data(df, 'all_bond_data', if_exists='replace')

    def get_premium(self, symbol):
        print(symbol)
        df = ak.bond_zh_cov_value_analysis(symbol=symbol)
        df['code'] = symbol
        print(df)
        self.save_data(df, 'bond_premium')

    def get_daily_data(self, code: str):
        if code.startswith('11') or code.startswith('13'):
            symbol = 'sh' + code
        elif code.startswith('12'):
            symbol = 'sz' + code
        else:
            return

        df = ak.bond_zh_hs_cov_daily(symbol=symbol)
        df['code'] = code
        self.save_data(df, 'bond_daily_data')

    def get_stock_daily_data(self, code):
        df = ak.stock_zh_a_hist(symbol=code, start_date="20220101", end_date=datetime.now().strftime('%Y%m%d'))
        df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'turnover', 'amplitude',
                      'change_rate', 'change', 'turnover_rate']
        df['code'] = code
        self.save_data(df, 'stock_daily_data')

    def read_data(self, table_name):
        with sqlite3.connect('../future_data.db') as conn:
            df = pd.read_sql(f'select * from {table_name}', conn)
        return df

    def save_data(self, df, table_name, if_exists='append'):
        with sqlite3.connect('../future_data.db') as conn:
            df.to_sql(table_name, conn,  index=False, if_exists=if_exists)


if __name__ == '__main__':
    # BondData().process()
    BondData().get_all_bond()

