import sqlite3
import time

import akshare as ak
import matplotlib.pyplot as plt
import pandas as pd


with sqlite3.connect('../future_data.db') as conn:
    df_bond = pd.read_sql(f'select * from all_bond_data', conn)


def plt_premium(code, period='1'):
    if code.startswith('12'):
        symbol = "sz" + code
    elif code.startswith('11'):
        symbol = "sh" + code

    try:
        stock_code = df_bond.loc[df_bond['债券代码'] == code, '正股代码'].values[0]
        convert_price = df_bond.loc[df_bond['债券代码'] == code, '转股价'].values[0]

        bond_data = ak.bond_zh_hs_cov_min(symbol=symbol, period=period)
        bond_data['时间'] = pd.to_datetime(bond_data['时间'])
        stock_data = ak.stock_zh_a_hist_min_em(symbol=str(stock_code), period=period)
        stock_data['时间'] = pd.to_datetime(stock_data['时间'])

        df = pd.merge(stock_data[['时间', '收盘']], bond_data[['时间', '收盘']], on='时间')
        df['premium'] = df.eval(f'收盘_y * {convert_price} / 收盘_x / 100 - 1')
        print(df)

        plt.plot(df['premium'])
        plt.title(f'{code} {df.loc[0].时间} -> {df.loc[len(df)-1].时间}')
        plt.show()
        # plt.savefig(f'./pic/{code}.png')
        # plt.clf()
    except:
        return


plt_premium('110077')

# tar_bond = df_bond[df_bond['转股溢价率'] < 3]['债券代码'].tolist()
#
# for code in tar_bond:
#     print(code)
#     plt_premium(code=code)
#     time.sleep(0.3)
