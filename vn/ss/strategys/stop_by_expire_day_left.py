from a_songbo.vn.configs.vn_config import StopByExpireDayLeft_params


class StopByExpireDayLeft:

    def __init__(self, gateway, portfilioprocess):
        self.gateway = gateway
        self.portfilioprocess = portfilioprocess
        self.variety_book = portfilioprocess.variety_book

        self.configs = StopByExpireDayLeft_params

    def cal_signal(self, quote):
        instrument = quote['InstrumentID']
        print(instrument, 'StopByExpireDayLeft')


