import sqlite3

import akshare as ak
import pandas as pd
from sqlalchemy import text

# 获取以下品种主力连续，日频数据
symbol_dict = {
    'V0': 'PVC连续,dce', 'P0': '棕榈油连续,dce', 'B0': '豆二连续,dce', 'M0': '豆粕连续,dce', 'I0': '铁矿石连续,dce',
    'JD0': '鸡蛋连续,dce', 'L0': '塑料连续,dce', 'PP0': '聚丙烯连续,dce', 'FB0': '纤维板连续,dce', 'BB0': '胶合板连续,dce',
    'Y0': '豆油连续,dce', 'C0': '玉米连续,dce', 'A0': '豆一连续,dce', 'J0': '焦炭连续,dce', 'JM0': '焦煤连续,dce',
    'CS0': '淀粉连续,dce', 'EG0': '乙二醇连续,dce', 'RR0': '粳米连续,dce', 'EB0': '苯乙烯连续,dce', 'TA0': 'PTA连续,czce',
    'OI0': '菜油连续,czce', 'RS2007': '菜籽2007连续,czce', 'RM0': '菜粕连续,czce', 'ZC0': '动力煤连续,czce', 'WH0': '强麦连续,czce',
    'JR2001': '粳稻2001连续,czce', 'SR0': '白糖连续,czce', 'CF0': '棉花连续,czce', 'RI0': '早籼稻连续,czce', 'MA0': '甲醇连续,czce',
    'FG0': '玻璃连续,czce', 'LR2001': '晚籼稻2001连续,czce', 'SF0': '硅铁连续,czce', 'SM0': '锰硅连续,czce', 'CY0': '棉纱连续,czce',
    'AP0': '苹果连续,czce', 'CJ0': '红枣连续,czce', 'UR0': '尿素连续,czce', 'SA0': '纯碱连续,czce', 'FU0': '燃料油连续,shfe',
    'SC0': '上海原油连续,ine', 'AL0': '铝连续,shfe', 'RU0': '天然橡胶连续,shfe', 'ZN0': '沪锌连续,shfe', 'CU0': '铜连续,shfe',
    'AU2006': '黄金2006连续,shfe', 'RB0': '螺纹钢连续,shfe', 'WR2001': '线材2001连续,shfe', 'PB0': '铅连续,shfe',
    'AG2006': '白银2006连续,shfe', 'BU0': '沥青连续,shfe', 'HC0': '热轧卷板连续,shfe', 'SN0': '锡连续,shfe',
    'NI2002': '镍2002连续,shfe', 'SP0': '纸浆连续,shfe', 'NR0': '20号胶连续,ine', 'SS0': '不锈钢连续,shfe'
}

delete_date = {'淀粉连续': [pd.to_datetime('2017-05-25')]}

# 创建一个 SQLite 连接(如果数据库不存在，它将被创建)
with sqlite3.connect('future_data.db') as conn:
    for k, v in symbol_dict.items():
        print(k, v)
        df = ak.futures_main_sina(symbol=k)
        # 格式化列名
        df = df.rename(
            columns={"日期": "date", "开盘价": "open_price", "最高价": "high_price",
                     "最低价": "low_price", "收盘价": "close_price",
                     "成交量": "volume", "持仓量": "open_interest",
                     "动态结算价": "dynamic_price", "品种": "variety",
                     "合约名称": "variety_name", "交易所": "exchange_type"})
        df['variety'] = k
        variety_name = v.split(',')[0]
        df['variety_name'] = variety_name
        df['exchange_type'] = v.split(',')[1]
        df['date'] = pd.to_datetime(df['date'])

        if variety_name in delete_date.keys():
            df = df[~df['date'].isin(delete_date[variety_name])]

        df.to_sql('future_daily_data', conn, if_exists='append', index=False)
        # quit()
