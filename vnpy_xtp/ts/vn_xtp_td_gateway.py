import time

from vn_xtp_td_api import XtpTdApi


class XtpTdGateway():
    def __init__(self):

        self.xtp_api = XtpTdApi(self)

    def write_log(self,message):
        print(message)

    def write_error(self,message,error):
        print(f'{message} {error}')

    def on_account(self,data):
        print(f'on_account:data={data}')


# python /byt_pub/a_songbo/vnpy_xtp/ts/vn_xtp_td_gateway.py
if __name__ == '__main__':
    x = XtpTdGateway()

    time.sleep(3)
    x.xtp_api.query_account()

    time.sleep(3)
    x.xtp_api.query_position()

    while 1:
        pass


