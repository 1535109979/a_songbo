from sqlalchemy import Column, VARCHAR, DECIMAL, BIGINT, INT, MetaData, Table, PrimaryKeyConstraint


MapKey = {'交易日': 'trading_day', '合约代码': 'name', '交易所代码': 'exchange', '合约在交易所的代码': 'symbol',
               '最新价': 'last_price',
               '上次结算价': 'pre_settlement_price', '昨收盘': 'pre_close',
               '昨持仓量': 'pre_open_interest', '今开盘': 'open_price', '最高价': 'high_price', '最低价': 'low_price',
               '数量': 'volume',
               '成交金额': 'turn_over', '持仓量': 'open_interest', '今收盘': 'close_price',
               '本次结算价': 'SettlementPrice',
               '涨停板价': 'limit_up', '跌停板价': 'limit_down', '昨虚实度': 'PreDelta', '今虚实度': 'CurrDelta',
               '最后修改时间': 'UpdateTime', '最后修改毫秒': 'UpdateMillisec', '申买价一': 'bid_price_1',
               '申买量一': 'bid_volume_1',
               '申卖价一': 'ask_price_1', '申卖量一': 'ask_volume_1', '申买价二': 'bid_price_2',
               '申买量二': 'bid_volume_2',
               '申卖价二': 'ask_price_2', '申卖量二': 'ask_volume_2', '申买价三': 'bid_price_3',
               '申买量三': 'bid_volume_3',
               '申卖价三': 'ask_price_3', '申卖量三': 'ask_volume_3', '申买价四': 'bid_price_4',
               '申买量四': 'bid_volume_4',
               '申卖价四': 'ask_price_4', '申卖量四': 'ask_volume_4', '申买价五': 'bid_price_5',
               '申买量五': 'bid_volume_5',
               '申卖价五': 'ask_price_5', '申卖量五': 'ask_volume_5', '当日均价': 'AveragePrice',
               '业务日期': 'ActionDay'}

SaveKey = ['id', 'localtime', 'datetime', 'trading_day', 'name', 'exchange', 'instrument_category',
             'volume', 'turn_over', 'open_interest', 'last_price', 'limit_up', 'limit_down',
             'open_price', 'high_price', 'low_price', 'close_price',
             'pre_open_interest', 'pre_settlement_price', 'pre_close', 'bid_price_1',
             'bid_volume_1', 'ask_price_1', 'ask_volume_1', 'bid_price_2',
             'bid_volume_2', 'ask_price_2', 'ask_volume_2', 'bid_price_3',
             'bid_volume_3', 'ask_price_3', 'ask_volume_3', 'bid_price_4',
             'bid_volume_4', 'ask_price_4', 'ask_volume_4', 'bid_price_5',
             'bid_volume_5', 'ask_price_5', 'ask_volume_5',
             ]


SaveType = {'id': BIGINT, 'localtime': DECIMAL(16, 3), 'datetime': VARCHAR(24), 'trading_day': INT,
                 'name': VARCHAR(16), 'exchange': VARCHAR(16), 'instrument_category': VARCHAR(16)}

Float_Keys = set(SaveKey) - set(SaveType)

for i in Float_Keys:
    SaveType[i] = DECIMAL(24, 8)

SaveType = {x:SaveType[x] for x in SaveKey}


EXCHANGE_MAP = {'a': 'dce', 'ag': 'shfe', 'al': 'shfe', 'ap': 'czce', 'au': 'shfe', 'b': 'dce', 'bu': 'shfe',
                'c': 'dce', 'cf': 'czce', 'cj': 'czce', 'cs': 'dce', 'cu': 'shfe', 'cy': 'czce', 'eb': 'dce',
                'eg': 'dce', 'fb': 'dce', 'fg': 'czce', 'fu': 'shfe', 'hc': 'shfe', 'i': 'dce', 'j': 'dce', 'jd': 'dce',
                'jm': 'dce', 'l': 'dce', 'm': 'dce', 'ma': 'czce', 'ni': 'shfe', 'oi': 'czce', 'p': 'dce', 'pb': 'shfe',
                'pp': 'dce', 'rb': 'shfe', 'rm': 'czce', 'rr': 'dce', 'rs': 'czce', 'ru': 'shfe', 'sa': 'czce',
                'sc': 'ine', 'sf': 'czce', 'sm': 'czce', 'sn': 'shfe', 'sp': 'shfe', 'sr': 'czce', 'ss': 'shfe',
                'ta': 'czce', 'ur': 'czce', 'v': 'dce', 'wh': 'czce', 'wr': 'shfe', 'y': 'dce', 'zc': 'czce',
                'zn': 'shfe', 'lr': 'czce', 'pm': 'czce', 'jr': 'czce', 'ri': 'czce', 'bb': 'dce', 'pg': 'dce',
                'lu': 'ine', 'nr': 'ine', 'pf': 'czce', 'bc': 'ine', 'lh': 'dce', 'pk': 'czce', }


