import sqlite3

import matplotlib.pyplot as plt
import pandas
import pandas as pd

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 500)

table_map = {'bond': 'all_bond_min', 'stock': 'all_bond_stock_min'}


def read_bond_min(code='113578', table_name='all_bond_min'):
    with sqlite3.connect('data/future_data_min.db') as connn:
        sql = f'SELECT order_book_id,datetime,close FROM {table_name} where order_book_id like "{code}%"'
        data = pd.read_sql(sql, connn)
        return data


def process_data(bond_code='113578', stock_code='603030', convert_price=3.2):
    df_bond = read_bond_min(code=bond_code, table_name=table_map['bond'])
    df_bond.columns = ['bond_code', 'datetime', 'bond_close']
    df_stock = read_bond_min(code=stock_code, table_name=table_map['stock'])
    df_stock.columns = ['stock_code', 'datetime', 'stock_close']

    df = pd.merge(df_bond, df_stock, how='inner', on='datetime')
    df['premium'] = df.eval(f'(bond_close * {convert_price} / stock_close / 100 - 1) * 100')
    print(df)

    plt.title(f'{bond_code}-{stock_code}')
    plt.plot(df['premium'].tail(5000))
    plt.show()


if __name__ == '__main__':
    bond_code = '113535'
    stock_code = '603278'
    convert_price = 9.59
    process_data(bond_code, stock_code, convert_price)
