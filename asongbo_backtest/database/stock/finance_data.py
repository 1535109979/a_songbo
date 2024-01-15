import sqlite3

import pandas
import pandas as pd
import requests
from tqdm import tqdm

pandas.set_option("expand_frame_repr", False)      #打印数据不折叠
pandas.set_option("display.max_rows", 2000)


def save_to_db(df, table_name):
    with sqlite3.connect('../future_data.db') as conn:
        df.to_sql(table_name, conn, if_exists='append', index=False)


def get_balance_sheet(date):
    table_name_map = {'RPT_DMSK_FN_BALANCE': 'balance_sheet',
                      'RPT_DMSK_FN_INCOME': 'income_sheet',
                      'RPT_DMSK_FN_CASHFLOW': 'cashflow_sheet'}

    for reportName in ['RPT_DMSK_FN_BALANCE', 'RPT_DMSK_FN_INCOME', 'RPT_DMSK_FN_CASHFLOW']:
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "sortColumns": "NOTICE_DATE,SECURITY_CODE",
            "sortTypes": "-1,-1",
            "pageSize": "500",
            "pageNumber": "1",
            "reportName": reportName,
            "columns": "ALL",
            "filter": f"""(SECURITY_TYPE_CODE in ("058001001","058001008"))(TRADE_MARKET_CODE!="069001017")(REPORT_DATE='{'-'.join([date[:4], date[4:6], date[6:]])}')""",
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        page_num = data_json["result"]["pages"]
        big_df = pd.DataFrame()
        for page in range(1, page_num + 1):
            params.update(
                {
                    "pageNumber": page,
                }
            )
            r = requests.get(url, params=params)
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["result"]["data"])
            big_df = pd.concat([big_df, temp_df], ignore_index=True)

        df = big_df.reset_index(drop=True)
        # print(df)
        save_to_db(df, table_name_map[reportName])


def read_save_date():
    with sqlite3.connect('../future_data.db') as conn:
        sql = 'select distinct REPORT_DATE from balance_sheet'
        date_list = pd.read_sql(sql, conn)['REPORT_DATE'].tolist()
    return sorted(date_list)


if __name__ == '__main__':
    date_list = read_save_date()
    print(date_list)

    days = ['0331', '0630', '0930', '1231']
    for year in range(2015, 2024):
        for day in days:
            date = str(year) + day
            if str(pd.to_datetime(date)) in date_list:
                continue

            print(date)
            get_balance_sheet(date)

