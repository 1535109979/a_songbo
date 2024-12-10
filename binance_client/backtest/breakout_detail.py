import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas
import pandas as pd

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)

# 当前价格 低于 前 n 分钟最小值，做多
# 当前价格 高于 前 n 分钟最大值，做空
# 取 前 roll_mean_period 分钟 均值 为 均线值
# 当持有 多头 时：满足 最新价格 > period 分钟前均线值 > period * 2 分钟前均线值，不做反手交易
# 当持有 空头 时：满足 最新价格 < period 分钟前均线值 < period * 2 分钟前均线值，不做反手交易


def read_db():
    import pandas as pd
    from sqlalchemy import create_engine, text

    engine = create_engine(
        'mysql+pymysql://app:6urA&D$%ji66WuHp@sh-cdb-peeq202o.sql.tencentcdb.com:59964/app?charset=utf8mb4')

    with engine.connect() as conn:
        sql = "select instrument, min_price_step from instrument_config where instrument_category = 'DIGICCY_FUTURES' and status = 'ENABLE' order by status, updated_time desc, exchange_type;"

        df = pd.read_sql(text(sql), con=conn)
    return df


df = read_db()
df = df.set_index('instrument')
min_price_step_map = df['min_price_step'].to_dict()



stop_loss_rate = 0.9
commision = 0.0006
trade_first = True
n = 400
roll_mean_period = 120
period = 860

if_trend = True
if not if_trend:
    period = 0
    roll_mean_period = 0

symbol = 'rlcusdt'
step_price = float(min_price_step_map[symbol.upper()])
start_time = '2024-01-01 00:00:00'

with sqlite3.connect('binance_quote_data.db') as conn:
    df = pd.read_sql(f'select * from future_{symbol} where start_time >= "{start_time}" order by start_time DESC', conn)

df = df.sort_values(by='start_time').reset_index(drop=True)
start_time = df.loc[0].start_time
end_time = df.loc[len(df)-1].start_time
df['close'] = df['close'].astype(float)

position = None
account_value = 1
account_value_list = []
long_rate = []
short_rate = []

time_list = df['start_time'].tolist()
close_list = df['close'].tolist()
df['roll_mean'] = df['close'].rolling(roll_mean_period).mean()
close_roll_mean_list = df['roll_mean'].tolist()

df_trade = pd.DataFrame(columns=['time', 'offset', 'dir', 'close', 'account_value'])

for i, close in enumerate(close_list):

    if i < max(n, 2 * period):
        continue

    time = time_list[i]
    last_n = close_list[int(i - n): i]
    last_n_max = max(last_n)
    last_n_min = min(last_n)

    if position:
        flag = None
        if position[0] == 'long':
            rate = close / position[1] - 1
            flag = 'long'
            if if_trend:
                if close > close_roll_mean_list[i-period] > close_roll_mean_list[i-2*period]:
                    continue

        elif position[0] == 'short':
            rate = 1 - close / position[1]
            flag = 'short'
            if if_trend:
                if close < close_roll_mean_list[i-period] < close_roll_mean_list[i-2*period]:
                    continue

        if rate < - stop_loss_rate:
            position = None
            account_value += rate - 0.0002

            df_trade.loc[len(df_trade)] = [symbol, time, 'stop_close', flag, close, account_value]
            account_value_list.append(account_value)
            continue

    if close < last_n_min:
        if not position:
            position = ('long', close)
            account_value += -commision
            account_value_list.append(account_value)
            df_trade.loc[len(df_trade)] = [time, 'open', 'long', close, account_value]
        else:
            if position[0] == 'short':
                if trade_first:
                    account_value += 1 - (close + step_price) / (position[1]) - commision
                else:
                    account_value += 1 - close / position[1] - commision
                df_trade.loc[len(df_trade)] = [time, 'close', 'short', close, account_value]

                short_rate.append(1 - close / position[1])
                account_value_list.append(account_value)
                position = ('long', close)
                account_value += -commision
                df_trade.loc[len(df_trade)] = [time, 'open', 'long', close, account_value]

    elif close > last_n_max:
        if not position:
            position = ('short', close)
            account_value += -commision
            account_value_list.append(account_value)

            df_trade.loc[len(df_trade)] = [time, 'open', 'short', close, account_value]
        else:
            if position[0] == 'long':
                if trade_first:
                    account_value += (close - step_price) / (position[1]) - 1 - commision
                else:
                    account_value += close / position[1] - 1 - commision
                df_trade.loc[len(df_trade)] = [time, 'close', 'long', close, account_value]

                long_rate.append(close / position[1] - 1)
                account_value_list.append(account_value)

                position = ('short', close)
                account_value += -commision
                df_trade.loc[len(df_trade)] = [time, 'open', 'short', close, account_value]

print(df_trade)


def cal_sharpe(account_list):
    daily_returns = np.array(account_list[1:]) / np.array(account_list[:-1]) - 1
    risk_free_rate = 0.02
    # 计算年化收益率
    annualized_return = np.mean(daily_returns) * 252
    # 计算年化标准差
    annualized_volatility = np.std(daily_returns) * np.sqrt(252)
    # 计算夏普比率
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
    print("Annualized Return:", annualized_return)
    print("Annualized Volatility:", annualized_volatility)
    print("Sharpe Ratio:", sharpe_ratio)
    return round(sharpe_ratio, 2)


def cal_loss(account_list):
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error

    model = LinearRegression()
    x_values = np.arange(len(account_list)).reshape(-1, 1)
    y_values = np.array(account_list)
    model.fit(x_values,y_values )
    y_pred = model.predict(x_values)
    loss = mean_squared_error(y_values, y_pred)
    return round(loss, 2)


sharpe_ratio = cal_sharpe(account_value_list)
loss = cal_loss(account_value_list)

loss_rate = [x for x in long_rate + short_rate if x<0]
plt.plot(loss_rate)
plt.savefig('loss_rate' + f'/{symbol}.jpg')
plt.clf()

plt.plot(account_value_list)

plt.title(f'{start_time}->{end_time} tradetimes={len(account_value_list)}  loss={loss}\n '
          f'{symbol} n={n} c={commision} sl={stop_loss_rate} p={period} rp={roll_mean_period} {sharpe_ratio}')
plt.show()

