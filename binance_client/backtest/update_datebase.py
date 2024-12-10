import sqlite3
from datetime import datetime, timedelta

import pandas
import pandas as pd
from binance.spot import Spot as Client
from binance.um_futures import UMFutures

pandas.set_option("expand_frame_repr", False)


class BinanceData:
    def __init__(self, mode='future'):
        self.spot_client = Client()
        self.future_client = UMFutures()
        self.mode = mode

    def download_data(self, start_time, end_time, symbol='BTCUSDT', interval='1m'):
        st_time = (datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=1)).timestamp()
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').timestamp()

        try:
            while st_time < end_time:
                if self.mode == 'spot':
                    df = self.get_spot_data(st_time, symbol, interval)
                elif self.mode == 'future':
                    df = self.get_future_data(st_time, symbol, interval)
                self.save_data(df, table_name=self.mode+'_'+symbol.lower())
                st_time = st_time + 1000 * 60
        except:
            print('error:', symbol)

    def save_data(self, df, table_name='spot_data'):
        with sqlite3.connect('/Users/edy/byt_pub/a_songbo/binance_client/backtest/binance_quote_data.db') as conn:
            df.to_sql(table_name, conn, if_exists='append', index=False)

    def get_future_data(self, st_time, symbol='BTCUSDT', interval='1m'):
        data = self.future_client.klines(symbol, interval, limit=1000, startTime=int(st_time) * 1000)
        df = pandas.DataFrame(data)
        df.columns = ['start_time', 'open', 'high', 'low', 'close', 'vol', 'end_time',
                      'quote_asset_vol', 'number_of_trade', 'base_asset_volume', 'quote_asset_volume', 'n']
        df['start_time'] = df['start_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
        df['end_time'] = df['end_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
        return df

    def get_spot_data(self, st_time, symbol='BTCUSDT', interval='1m'):
        data = self.spot_client.klines(symbol, interval, limit=1000, startTime=int(st_time) * 1000)
        df = pandas.DataFrame(data)
        df.columns = ['start_time', 'open', 'high', 'low', 'close', 'vol', 'end_time',
                      'quote_asset_vol', 'number_of_trade', 'base_asset_volume', 'quote_asset_volume', 'n']
        df['start_time'] = df['start_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
        df['end_time'] = df['end_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
        return df


def update_data():
    with sqlite3.connect('/Users/edy/byt_pub/a_songbo/binance_client/backtest/binance_quote_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # for table in tables:
        #     table_name = table[0]
        for table in ['LTCUSDT', 'EOSUSDT', 'AEVOUSDT', 'APEUSDT', 'BANDUSDT', 'CELRUSDT', 'ONDOUSDT', 'NFPUSDT',
                      'PORTALUSDT', 'ETHUSDT', 'RLCUSDT', 'MOVRUSDT']:
            table_name = 'future_' + table.lower()
            cursor.execute(f"SELECT MAX(start_time) FROM {table_name};")
            max_time = cursor.fetchone()[0]
            symbol = table_name.split('_')[1]
            print(symbol, max_time, datetime.now())
            BinanceData().download_data(max_time, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol=symbol.upper())


if __name__ == '__main__':
    update_data()


