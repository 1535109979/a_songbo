from byt_config.utils import config_loader
from byt_persistent.dao.base_dao import get_conf_dbm,get_md_dbm
import pandas as pd
import matplotlib.pyplot as plt


def connect_db():
    config_loader.load_config()
    # dbm = get_conf_dbm()
    dbm = get_md_dbm()
    return dbm


def get_data():
    dbm = connect_db()
    df = dbm.query_data_frame('tick_futures_shfe_rb2303')[['datetime','last_price']]
    print(df['datetime'].tolist)


if __name__ == '__main__':
    get_data()