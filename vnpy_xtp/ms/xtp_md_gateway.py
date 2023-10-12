import time

from vn_xtp_md_api import VnXtpMdApi


class XtpMdGateway():
    def __init__(self):

        self.xtp_api = VnXtpMdApi(self)

    def write_log(self,message):
        print(message)

    def write_error(self,message,error):
        print(f'{message} {error}')

    def subscribe(self):
        self.xtp_api.subscribe(symbol='600487')

    def on_quote(self,data):
        """{'exchange_id': 1, 'ticker': '600487', 'last_price': 15.700000000000001, 'pre_close_price': 15.82, 'open_price': 15.950000000000001, 'high_price': 15.98, 'low_price': 15.700000000000001, 'close_price': 0.0, 'pre_total_long_positon': 0, 'total_long_positon': 0, 'pre_settl_price': 0.0, 'settl_price': 0.0, 'upper_limit_price': 17.4, 'lower_limit_price': 14.24, 'pre_delta': 0.0, 'curr_delta': 0.0, 'data_time': 20230717131915000, 'qty': 130963397, 'turnover': 2073753012.7400002, 'avg_price': 15.834600050424779, 'trades_count': 116827, 'data_type_v2': 2, 'ask': [15.71, 15.72, 15.73, 15.74, 15.75, 15.76, 15.77, 15.780000000000001, 15.790000000000001, 15.8], 'bid': [15.700000000000001, 15.69, 15.68, 15.67, 15.66, 15.65, 15.64, 15.63, 15.620000000000001, 15.610000000000001], 'bid_qty': [511700, 124600, 421500, 111000, 207800, 164400, 21000, 41600, 134000, 125600], 'ask_qty': [136200, 52300, 42600, 25500, 158100, 44200, 17900, 44600, 27200, 98600]}"""
        print(f'收到行情：',data)


# python /byt_pub/a_songbo/vnpy_xtp/ms/xtp_md_gateway.py
if __name__ == '__main__':
    x = XtpMdGateway()

    time.sleep(3)

    x.xtp_api.subscribe()

    time.sleep(20)
    x.xtp_api.cancel_subscribe()

    while 1:
        pass




