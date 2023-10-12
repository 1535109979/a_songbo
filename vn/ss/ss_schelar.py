import time
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from a_songbo.vn.configs.vn_config import time_configs
from a_songbo.vn.data.process_sqlite import Options, SqliteDatabaseManage, Minprice, HistoryPrice
from a_songbo.vn.util.sys_exception import common_exception

import warnings
warnings.filterwarnings('ignore')


class SsSchelar:
    def __init__(self, gateway):
        self.gateway = gateway

        self.date = datetime.now().strftime('%Y-%m-%d')
        self.start_trading_times = time_configs['start_trading_times']
        self.end_trading_times = time_configs['end_trading_times']
        self.save_imp_times = time_configs['save_imp_times']

        self.scheduler = BlockingScheduler()

    def run(self):
        for ti in self.start_trading_times:
            self.scheduler.add_job(self.start_trading, 'date', run_date=self.date + ' ' + ti)

        for ti in self.end_trading_times:
            self.scheduler.add_job(self.end_trading, 'date', run_date=self.date + ' ' + ti)

        for ti in self.save_imp_times:
            self.scheduler.add_job(self.save_imp, 'date', run_date=self.date + ' ' + ti)

        self.scheduler.add_job(self.check_last_quote, 'interval', seconds=30)

        self.scheduler.start()

    @common_exception(log_flag=True)
    def start_trading(self):
        self.gateway.in_tradinng_time = True
        self.gateway.send_msg('进入可交易时间')

    @common_exception(log_flag=True)
    def end_trading(self):
        self.gateway.in_tradinng_time = False
        self.gateway.send_msg('进入不可交易时间,停止交易')

    @common_exception(log_flag=True)
    def save_imp(self):
        self.gateway.saved_price = {k: {'price': round(float(v['LastPrice']), 2), 'timestamp': v['quote_time']}
                                    for k, v in self.gateway.last_price.items()}

        price_save_list = []
        for instrument, value in self.gateway.saved_price.items():
            price_save_list.append({
                'instrument': instrument,
                'price': value['price'],
                'timestamp': value['timestamp'],
            })
        with SqliteDatabaseManage().get_connect().atomic():
            HistoryPrice.delete().execute()
            HistoryPrice.insert_many(price_save_list).execute()

        # imp_save_list = []
        # for instrument, value in self.gateway.last_imp.items():
        #     imp_save_list.append({
        #         'instrument': instrument,
        #         'imp': value['imp'],
        #         'timestamp': value['timestamp'],
        #     })
        # with SqliteDatabaseManage().get_connect().atomic():
        #     Options.delete().execute()
        #     Options.insert_many(imp_save_list).execute()
        # self.gateway.saved_imp = self.gateway.last_imp

        min_price_save_list = []
        for instrument, value in self.gateway.min_price.items():
            min_price_save_list.append({
                'instrument': instrument,
                'price': value['price'],
                'timestamp': value['timestamp'],
            })
        with SqliteDatabaseManage().get_connect().atomic():
            Minprice.delete().execute()
            Minprice.insert_many(min_price_save_list).execute()

        self.gateway.send_msg(f'保存{len(min_price_save_list)}条最低价  \n'
                              f'保存{len(self.gateway.saved_price)}条期权价格')

    @common_exception(log_flag=True)
    def check_last_quote(self):
        if self.gateway.in_tradinng_time and len(self.gateway.last_price):
            timestamps = [float(v['timestamp']) for k, v in self.gateway.last_price.items()]
            time_diff = time.time() - max(timestamps)
            self.gateway.logger.info(f'check_last_quote time_diff={time_diff}')
            if time_diff > 60:
                self.gateway.send_msg('!!! 超过60秒没有收到任何行情 !!!', isatall=True)


if __name__ == '__main__':
    data = [{'instrument': 'ru2311P14000', 'imp': 0.292749, 'timestamp': 1695365538.5},
            {'instrument': 'sc2312C780', 'imp': 0.282193, 'timestamp': 1695365539.0},
            {'instrument': 'ru2311C14500', 'imp': 0.289536, 'timestamp': 1695365539.0},
            {'instrument': 'al2311C21000', 'imp': 0.181318, 'timestamp': 1695365536.0},
            {'instrument': 'zn2311C23800', 'imp': 0.18724, 'timestamp': 1695365539.5}]

    from peewee import fn

    query = Options.select(Options.instrument, Options.imp, fn.MAX(Options.timestamp).alias('max_timestamp')).group_by(
        Options.instrument)
    result = [(row.instrument, row.imp, row.max_timestamp) for row in query]
    imp_dict = {row.instrument: {'imp': row.imp, 'timestamp': row.max_timestamp} for row in query}
    print(result)
    print(imp_dict)

    # with SqliteDatabaseManage().get_connect().atomic():
    #     Options.insert_many(data).execute()

    quit()
