from pathlib import Path
from typing import Dict

from vnpy.trader.constant import Exchange
from vnpy.trader.utility import _get_trader_dir

from vnpy_xtp.api import TdApi

# 日志级别映射
LOGLEVEL_VT2XTP = {
    "FATAL": 0,
    "ERROR": 1,
    "WARNING": 2,
    "INFO": 3,
    "DEBUG": 4,
    "TRACE": 5,
}

setting = {
    "账号": "253191002712",
    "密码": "JvVnf6jM",
    "客户号": '1',
    "行情地址": "119.3.103.38",
    "行情端口": "6002",
    "交易地址": "122.112.139.0",
    "交易端口": "6102",
    "授权码": "b8aa7173bba3470e390d787219b2112e",
    "行情协议": ["TCP", "UDP"],
    "日志级别": ["FATAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"],
}


class XtpTdApi(TdApi):

    def __init__(self, gateway):
        """"""
        super().__init__()

        self.gateway = gateway



        self.userid: str = setting["账号"]
        self.password: str = setting["密码"]
        self.client_id: int = int(setting["客户号"])
        self.server_ip: str = setting["行情地址"]
        self.server_port: int = int(setting["行情端口"])
        self.trader_ip: str = setting["交易地址"]
        self.trader_port: int = int(setting["交易端口"])
        self.software_key: str = setting["授权码"]
        self.protocol: int = 1
        self.log_level: int = LOGLEVEL_VT2XTP[setting["日志级别"][1]]

        self.connect_status: bool = False
        self.login_status: bool = False
        # 账户是否支持两融或者期权交易
        self.margin_trading = False

        self.session_id: int = 0
        self.reqid: int = 0

        self.connect()

    def connect(self):
        if not self.connect_status:
            path: str = '/Users/edy/.vntrader'
            self.createTraderApi(self.client_id, path, self.log_level)

            self.setSoftwareKey(self.software_key)
            self.subscribePublicTopic(0)
            self.login_server()
        else:
            self.gateway.write_log("交易接口已登录，请勿重复操作")

    def login_server(self) -> None:
        """登录"""
        n: int = self.login(
            self.trader_ip,
            self.trader_port,
            self.userid,
            self.password,
            self.protocol
        )
        if n:
            self.session_id = n
            self.connect_status = True
            self.login_status = True
            msg: str = f"交易服务器登录成功, 会话编号：{self.session_id}"
            self.init()
        else:
            error: dict = self.getApiLastError()
            msg: str = f"交易服务器登录失败，原因：{error['error_msg']}"

        self.gateway.write_log(msg)
        # self.query_option_info()

    def close(self) -> None:
        """关闭连接"""
        if self.connect_status:
            self.exit()

    def query_account(self) -> None:
        """查询资金"""
        if not self.connect_status:
            return

        self.reqid += 1
        self.queryAsset(self.session_id, self.reqid)

    def onQueryAsset(self,data: dict,error: dict,request: int,last: bool,session: int) -> None:
        """查询资金回报"""
        """{'total_asset': 999984162.0, 'buying_power': 999984162.0, 'security_asset': 0.0, 'fund_buy_amount': 15790.0, 'fund_buy_fee': 48.0, 'fund_sell_amount': 0.0, 'fund_sell_fee': 0.0, 'withholding_amount': 0.0, 'account_type': 0, 'frozen_margin': 0.0, 'frozen_exec_cash': 0.0, 'frozen_exec_fee': 0.0, 'pay_later': 0.0, 'preadva_pay': 0.0, 'orig_banlance': 0.0, 'banlance': 0.0, 'deposit_withdraw': 0.0, 'trade_netting': 0.0, 'captial_asset': 0.0, 'force_freeze_amount': 0.0, 'preferred_amount': 0.0, 'repay_stock_aval_banlance': 0.0, 'fund_order_data_charges': 0.0, 'fund_cancel_data_charges': 0.0, 'exchange_cur_risk_degree': 0.0, 'company_cur_risk_degree': 0.0, 'unknown': 0}"""
        self.gateway.on_account(data)

    def query_position(self) -> None:
        """查询持仓"""
        if not self.connect_status:
            return

        self.reqid += 1
        self.queryPosition("", self.session_id, self.reqid)

        if self.margin_trading:
            self.reqid += 1
            self.queryCreditDebtInfo(self.session_id, self.reqid)

    def onQueryPosition(self,data: dict,error: dict,request: int,last: bool,session: int) -> None:
        """查询持仓回报"""
        """{'ticker': '600487', 'ticker_name': '亨通光电', 'market': 2, 'total_qty': 1000, 'sellable_qty': 0, 'avg_price': 15.838, 'unrealized_pnl': 0.0, 'yesterday_position': 0, 'purchase_redeemable_qty': 1000, 'position_direction': 0, 'position_security_type': 0, 'executable_option': 0, 'lockable_position': 0, 'executable_underlying': 0, 'locked_position': 0, 'usable_locked_position': 0, 'profit_price': 15.838, 'buy_cost': 15838.0, 'profit_cost': 15838.0, 'unknown': 0}"""
        if data["market"] == 0:
            return

        print(f'查询持仓回报:data={data}')


