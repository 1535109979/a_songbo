import pandas
from tqsdk import TqApi, TqAuth, tafunc
from tqsdk.ta import OPTION_IMPV

api = TqApi(web_gui=True, auth=TqAuth("15605173271", "songbo1997"))
api = TqApi(auth=TqAuth("15605173271", "songbo1997"))

# ticks = api.get_tick_serial("SHFE.cu1812")
# ticks.datetime = ticks.datetime.map(tafunc.time_to_datetime)
# print(ticks)
#
# api.close()

# klines = api.get_kline_serial("SHFE.cu2002", 10)
# while True:
#     # 通过wait_update刷新数据
#     api.wait_update()
