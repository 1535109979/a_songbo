from datetime import datetime

from tqsdk import TqApi, TqAuth, tafunc


api = TqApi(auth=TqAuth("15605173271", "songbo1997"))

ticks = api.get_tick_serial("SHFE.rb2403",)

while api.wait_update():
    def transform_time(input_time):
        # print(input_time)
        # print(type(input_time))
        if type(input_time) == float:
            ts = input_time / 1e9
            # 转为datetime.datetime类型
            dt = datetime.fromtimestamp(ts)
            return dt
    ticks.datetime = ticks.datetime.map(transform_time)
    print(dict(ticks.loc[len(ticks)-1]))



