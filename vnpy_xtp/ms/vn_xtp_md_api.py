from pathlib import Path
from typing import Dict

from vnpy.trader.constant import Exchange
from vnpy.trader.utility import _get_trader_dir

from vnpy_xtp.api import MdApi

EXCHANGE_XTP2VT: Dict[int, Exchange] = {
    1: Exchange.SSE,
    2: Exchange.SZSE,
}
EXCHANGE_VT2XTP: Dict[Exchange, int] = {v: k for k, v in EXCHANGE_XTP2VT.items()}

# 日志级别映射
LOGLEVEL_VT2XTP = {
    "FATAL": 0,
    "ERROR": 1,
    "WARNING": 2,
    "INFO": 3,
    "DEBUG": 4,
    "TRACE": 5,
}

TRADER_DIR, TEMP_DIR = _get_trader_dir(".vntrader")


def get_folder_path(folder_name: str) -> Path:
    """
    Get path for temp folder with folder name.
    """
    folder_path: Path = TEMP_DIR.joinpath(folder_name)
    if not folder_path.exists():
        folder_path.mkdir()
    return folder_path


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


class VnXtpMdApi(MdApi):
    def __init__(self, gateway=None):
        """构造函数"""
        super().__init__()

        self.gateway = gateway
        self.gateway_name = 'xtp'

        # 获取柜台配置
        self.configs: dict = gateway.get_api_configs()

        self.userid: str = setting["账号"]
        self.password: str = setting["密码"]
        self.client_id: int = int(setting["客户号"])
        self.server_ip: str = setting["行情地址"]
        self.server_port: int = int(setting["行情端口"])
        self.trader_ip: str = setting["交易地址"]
        self.trader_port: int = int(setting["交易端口"])
        self.software_key: str = setting["授权码"]
        self.log_level: int = LOGLEVEL_VT2XTP[setting["日志级别"][1]]
        self.protocol: int = 1

        self.connect_status: bool = False
        self.login_status: bool = False

        self.connect()

    def connect(self):
        if not self.connect_status:
            path: str = '/Users/edy/.vntrader'
            self.createQuoteApi(self.client_id, path, self.log_level)
            self.login_server()
        else:
            self.gateway.write_log("行情接口已登录，请勿重复操作")

    def login_server(self) -> None:
        """用户登录"""
        n: int = self.login(
            self.server_ip,
            self.server_port,
            self.userid,
            self.password,
            self.protocol,
            ""
        )

        if not n:
            self.connect_status = True
            self.login_status = True
            msg: str = "行情服务器登录成功"
            self.init()
            # self.query_contract()
        else:
            error: dict = self.getApiLastError()
            msg: str = f"行情服务器登录失败，原因：{error['error_msg']}"

        self.gateway.write_log(msg)

    def onDisconnected(self, reason: int) -> None:
        """服务器连接断开回报"""
        self.connect_status = False
        self.login_status = False
        self.gateway.write_log(f"行情服务器连接断开, 原因{reason}")

        self.login_server()

    def close(self) -> None:
        """关闭连接"""
        if self.connect_status:
            self.exit()

    def query_contract(self) -> None:
        """查询合约信息"""
        for exchange_id in EXCHANGE_XTP2VT.keys():
            print('exchange_id', exchange_id)
            self.queryAllTickers(exchange_id)

    def onQueryAllTickers(self, data: dict, error: dict, last: bool) -> None:
        """查询合约回报"""
        """{'exchange_id': 1, 'ticker': '600487', 'ticker_name': '亨通光电', 'ticker_type': 0, 'pre_close_price': 15.82, 
        'upper_limit_price': 17.400000000000002, 'lower_limit_price': 14.24, 'price_tick': 0.01, 'buy_qty_unit': 100, 
        'sell_qty_unit': 1} error_old={} last=False"""
        self.gateway.write_log(f'data={data} error_old={error} last={last}')

        if last:
            self.gateway.write_log(f"合约信息查询成功")

    def onError(self, error: dict) -> None:
        """请求报错回报"""
        self.gateway.write_error("行情接口报错", error)

    def subscribe(self, symbol='600487',exchange=Exchange.SSE) -> None:
        """订阅行情"""
        if self.login_status:
            xtp_exchange: int = EXCHANGE_VT2XTP.get(exchange, "")
            self.subscribeMarketData(symbol, 1, xtp_exchange)

    def onSubMarketData(self, data: dict, error: dict, last: bool) -> None:
        """订阅行情回报"""
        if not error or not error["error_id"]:
            self.gateway.write_log(f'订阅行情回报:data={data},error_old={error},last={last}')
            return

        self.gateway.write_error("行情订阅失败", error)

    def cancel_subscribe(self, symbol='600487',exchange=Exchange.SSE) -> None:
        """订阅行情"""
        if self.login_status:
            xtp_exchange: int = EXCHANGE_VT2XTP.get(exchange, "")
            self.unSubscribeMarketData(symbol, 1, xtp_exchange)

    def onUnSubMarketData(self, data: dict, error: dict, last: bool) -> None:
        """订阅行情回报"""
        if not error or not error["error_id"]:
            self.gateway.write_log(f'取消订阅行情回报:data={data},error_old={error},last={last}')
            return

    def onDepthMarketData(self, data: dict) -> None:
        """行情推送回报"""
        self.gateway.on_quote(data)


