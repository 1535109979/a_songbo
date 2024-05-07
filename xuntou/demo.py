# from xtquant import xtdatacenter as xtdc
# xtdc.set_token('240157cd776c0fe3383d186fc2f249069ba116c1')
# xtdc.init()

from xtquant import xtdata
import time


def my_download(stock_list, period, start_date='', end_date=''):
    '''
    用于显示下载进度
    '''
    if "d" in period:
        period = "1d"
    elif "m" in period:
        if int(period[0]) < 5:
            period = "1m"
        else:
            period = "5m"
    elif "tick" == period:
        pass
    else:
        raise KeyboardInterrupt("周期传入错误")

    n = 1
    num = len(stock_list)
    for i in stock_list:
        print(f"当前正在下载{n}/{num}")

        xtdata.download_history_data(i, period, start_date, end_date)
        n += 1
    print("下载任务结束")


def do_subscribe_quote(stock_list: list, period: str):
    for i in stock_list:
        xtdata.subscribe_quote(i, period=period)
    time.sleep(1)  # 等待订阅完成


if __name__ == "__main__":

    start_date = '20231001'  # 格式"YYYYMMDD"，开始下载的日期，date = ""时全量下载
    end_date = ""
    period = "1d"

    need_download = 1  # 取数据是空值时，将need_download赋值为1，确保正确下载了历史数据

    code_list = ["000001.SZ", "600519.SH"]  # 股票列表

    if need_download:  # 判断要不要下载数据, gmd系列函数都是从本地读取历史数据,从服务器订阅获取最新数据
        my_download(code_list, period, start_date, end_date)

    ############ 仅获取历史行情 #####################
    count = -1  # 设置count参数，使gmd_ex返回全部数据
    data1 = xtdata.get_market_data_ex([], code_list, period=period, start_time=start_date, end_time=end_date)

    ############ 仅获取最新行情 #####################
    do_subscribe_quote(code_list, period)  # 设置订阅参数，使gmd_ex取到最新行情
    count = 1  # 设置count参数，使gmd_ex仅返回最新行情数据
    data2 = xtdata.get_market_data_ex([], code_list, period=period, start_time=start_date, end_time=end_date,
                                      count=1)  # count 设置为1，使返回值只包含最新行情

    ############ 获取历史行情+最新行情 #####################
    do_subscribe_quote(code_list, period)  # 设置订阅参数，使gmd_ex取到最新行情
    count = -1  # 设置count参数，使gmd_ex返回全部数据
    data3 = xtdata.get_market_data_ex([], code_list, period=period, start_time=start_date, end_time=end_date,
                                      count=-1)  # count 设置为1，使返回值只包含最新行情

    print(data1[code_list[0]].tail())  # 行情数据查看
    print(data2[code_list[0]].tail())
    print(data3[code_list[0]].tail())




