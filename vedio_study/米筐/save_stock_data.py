import sqlite3

import pandas
import pandas as pd
import rqdatac

rqdatac.init(username='15605173271', password='songbo1997')

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 500)


class StockData:
    def __init__(self):
        self.db_fp = 'data/stock_data.db'

    def process(self):
        # self.get_all_stock()

        df = self.read_sqlite_data(sql='select * from all_instrument where de_listed_date="0000-00-00" and type="CS"')
        stock_codes = df['order_book_id'].tolist()
        for stock_code in stock_codes:
            print(stock_code)
            # self.save_instrument_industry(stock_code)
            self.save_price(stock_code)
            # quit()

    def get_all_stock(self):
        """
        获取所有合约基础信息
        CS	Common Stock, 即股票
        ETF	Exchange Traded Fund, 即交易所交易基金
        LOF	Listed Open-Ended Fund，即上市型开放式基金 （以下分级基金已并入）
        INDX	Index, 即指数
        Future	Futures，即期货，包含股指、国债和商品期货
        Spot	Spot，即现货，目前包括上海黄金交易所现货合约
        Option	期权，包括目前国内已上市的全部期权合约
        Convertible	沪深两市场内有交易的可转债合约
        Repo	沪深两市交易所交易的回购合约
        """
        df = rqdatac.all_instruments(type=None, market='cn', date=None)
        self.save_to_sqlite(df, 'all_instrument', if_exists='replace')

    def save_price(self, order_book_ids):
        df = rqdatac.get_price(order_book_ids, start_date='20170101', end_date='20231113', frequency='1d')
        if not df is None:
            df = df.reset_index()
            self.save_to_sqlite(df, 'stock_daily_price')

    def save_instrument_industry(self, order_book_ids):
        df = rqdatac.get_instrument_industry(order_book_ids, source='citics_2019', level=0, date=None, market='cn')
        if not df is None:
            df = df.reset_index()
            self.save_to_sqlite(df, 'instrument_industry')

    def save_to_sqlite(self, df: pandas.DataFrame, table_name, if_exists='append'):
        with sqlite3.connect(self.db_fp) as connn:
            df.to_sql(table_name, connn, index=False, if_exists=if_exists)

    def read_sqlite_data(self, sql):
        with sqlite3.connect(self.db_fp) as connn:
            return pd.read_sql(sql, connn)

    def save_holder_number(self, order_book_ids, start_date=None, end_date=None):
        """
        :param order_book_ids:
        :param start_date: 开始日期，默认为去年当日
        :param end_date:   结束日期，默认为去年当日
        :return:
        order_book_ids	str	合约代码
        info_date	datetime.date	发布日期
        end_date	datetime.date	截止日期
        share_holders	float	股东总户数(户)
        avg_share_holders	float	户均持股数(股/户)
        a_share_holders	float	A 股股东户数(户)
        avg_a_share_holders	float	A 股股东户均持股数(股/户)
        avg_circulation_share_holders	float	无限售 A 股股东户均持股数(股/户)
        """
        df = rqdatac.get_holder_number(order_book_ids, start_date, end_date, market='cn')
        # self.save_to_sqlite(df, 'holder_number')
        return df


if __name__ == '__main__':
    StockData().process()
