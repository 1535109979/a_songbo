import os

ctp_setting = {
            "vn_config_home": os.path.join(os.path.expanduser('~'), ".vntrader"),
            'account_id': '210380', 'password': 'Songbo@1997', 'brokerid': '9999',
            'md_address': 'tcp://180.168.146.187:10212',
            'td_address': 'tcp://180.168.146.187:10202',
            # 'md_address': 'tcp://180.168.146.187:10131',
            # 'td_address': 'tcp://180.168.146.187:10130',
            'appid': 'simnow_client_test', 'auth_code': '0000000000000000', }

grid_trade_futures = ['rb2403', 'rb2401', 'rb2402', 'pb2403', 'pb2402', 'pb2401']

strategy_config = {
    'module_name': 'a_songbo.vn.ss.strategys',
    'avail_down': 100000,       # 可用资金最小值，低于改值不开仓
    'expire_day_left_period': [10, 30],
    'load_strategy_list': [
        'SellStrategy',
        'StopByMinPrice',
        # 'StopByExpireDayLeft',
    ],   # 加载策略

}

SellStrategy_params = {
    'sell_lot': 1,              # 每次下单 手
    'sell_imp_limit': 0.1,      # 卖出策略，隐含波动率阈值
}

StopByMinPrice_params = {
    'close_lot': 1,              # 每次下单 手
    'profit_stop_rate': 0.05,   # 盈利时从开仓后最低价 反弹比例
    'loss_stop_rate': 0.05
}

BuyStrategy_params = {
    'buy_lot': 1,
}

StopByExpireDayLeft_params = {
    'day_left_limit': 10      # 到期日只剩10天，直接平仓
}

time_configs = {
    'start_trading_times': ['09:03:00', '10:30:00', '13:30:00', '21:03:00'],
    'end_trading_times': ['10:15:00', '11:30:00', '15:00:00', '23:59:59'],
    'save_imp_times': ['09:30:00', '10:00:00', '11:00:00', '11:29:00', '14:00:00', '14:30:00', '15:00:00',
                       '15:55:00', '21:30:00', '22:00:00', '22:30:00', '23:00:00', '23:30:00', '23:59:00']
}

