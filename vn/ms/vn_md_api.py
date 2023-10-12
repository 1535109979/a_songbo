import time
from typing import TYPE_CHECKING
from datetime import datetime
from vnpy_ctp.api import MdApi


if TYPE_CHECKING:
    from a_songbo.Vnpy.ms.async_server.async_market_gateway import VnMarketGateway


class VnMdApi(MdApi):
    """
    createFtdcMdApi(arg0: str) -> None：创建一个行情API实例。
    exit() -> int：关闭行情API并释放资源。
    getTradingDay() -> str：获取当前交易日日期。
    init() -> None：初始化行情API实例。
    join() -> int：等待行情API线程结束运行。
    onFrontConnected() -> None：当与前置机建立起通信连接时调用。
    onFrontDisconnected(arg0: int) -> None：当与前置机断开连接时调用。
    onHeartBeatWarning(arg0: int) -> None：当心跳超时警告时调用。
    onRspError(arg0: dict, arg1: int, arg2: bool) -> None：错误应答时调用。
    onRspQryMulticastInstrument(arg0: dict, arg1: dict, arg2: int, arg3: bool) -> None：多播合约查询应答时调用。
    onRspSubForQuoteRsp(arg0: dict, arg1: dict, arg2: int, arg3: bool) -> None：订阅询价应答时调用。
    onRspSubMarketData(arg0: dict, arg1: dict, arg2: int, arg3: bool) -> None：订阅行情应答时调用。
    onRspUnSubForQuoteRsp(arg0: dict, arg1: dict, arg2: int, arg3: bool) -> None：取消订阅询价应答时调用。
    onRspUnSubMarketData(arg0: dict, arg1: dict, arg2: int, arg3: bool) -> None：取消订阅行情应答时调用。
    onRspUserLogin(arg0: dict, arg1: dict, arg2: int, arg3: bool) -> None：用户登录应答时调用。
    onRspUserLogout(arg0: dict, arg1: dict, arg2: int, arg3: bool) -> None：用户登出应答时调用。
    onRtnDepthMarketData(arg0: dict) -> None：深度行情推送时调用。
    onRtnForQuoteRsp(arg0: dict) -> None：询价推送时调用。
    registerFensUserInfo(arg0: dict) -> None：注册FENS用户信息。
    registerFront(arg0: str) -> None：注册前置机网络地址。
    registerNameServer(arg0: str) -> None：注册名字服务器网络地址。
    release() -> None：释放行情API实例所占用的资源。
    reqQryMulticastInstrument(arg0: dict, arg1: int) -> int：发起多播合约查询请求。
    reqUserLogin(arg0: dict, arg1: int) -> int：发起用户登录请求。
    reqUserLogout(arg0: dict, arg1: int) -> int：发起用户登出请求。
    subscribeForQuoteRsp(arg0: str) -> int：订阅询价。
    subscribeMarketData(arg0: str) -> int：订阅行情。
    unSubscribeForQuoteRsp(arg0: str) -> int：取消订阅询价。
    unSubscribeMarketData(arg0: str) -> int：取消订阅行情。
    """

    def __init__(self, gateway: "VnMarketGateway") -> None:
        super().__init__()

        self.gateway = gateway
        self.logger = self.gateway.logger
        self.configs = self.gateway.get_configs

        self.reqid: int = 0
        self.connect_status: bool = False
        self.login_status: bool = False

        self.userid: str = ""
        self.password: str = ""
        self.brokerid: str = ""
        self.current_date: str = datetime.now().strftime("%Y%m%d")

        self.connect_api()

    def connect_api(self):
        self.connect(self.configs['md_address'], self.configs['account_id'],
                     self.configs['password'], self.configs['brokerid'])

    def subscribe(self,symbol='rb2307') -> None:
        """订阅行情"""
        if self.login_status:
            self.gateway.logger.info(f'添加订阅：{symbol}')
            self.subscribeMarketData(symbol)

    def onRtnDepthMarketData(self, data: dict) -> None:
        """行情数据推送"""
        # self.gateway.logger.info(f'{data["InstrumentID"]}')
        self.gateway.on_quote(data)

    def onRspQryMulticastInstrument(self, data, error, n, last):
        self.gateway.logger.info(f'<onRspQryMulticastInstrument>data:{data},error:{error},n={n},last{last}')
        if not error['ErrorID']:
            for instrument in data.get('Instruments', []):
                self.instruments.append(instrument['InstrumentID'])

    def cancel_subscribe(self,symbol='rb2307'):
        self.unSubscribeMarketData(symbol)
        self.gateway.logger.info(f'取消订阅行情:{symbol}')

    def onRspSubMarketData(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """订阅行情回报"""
        if not error or not error["ErrorID"]:
            self.gateway.logger.info(f'成功添加订阅,data:{data},reqid:{reqid},last{last}')
            return

    def connect(self, address: str, userid: str, password: str, brokerid: str) -> None:
        """连接服务器"""
        self.userid = userid
        self.password = password
        self.brokerid = brokerid
        # 禁止重复发起连接，会导致异常崩溃
        if not self.connect_status:
            self.gateway.logger.info(f'行情服务器,开始连接:{address}')
            path = self.configs['vn_config_home']
            self.createFtdcMdApi((str(path) + "\\Md").encode("GBK"))
            self.registerFront(address)
            self.init()
            self.connect_status = True

    def onFrontConnected(self) -> None:
        """服务器连接成功回报"""
        self.gateway.logger.info('服务器连接成功，开始登陆')
        self.login()

    def login(self) -> None:
        """用户登录"""
        self.ctp_req: dict = {
            "UserID": self.userid,
            "Password": self.password,
            "BrokerID": self.brokerid
        }

        self.reqid += 1
        self.reqUserLogin(self.ctp_req, self.reqid)

    def onRspUserLogin(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """用户登录请求回报"""
        if not error["ErrorID"]:
            self.login_status = True
            self.gateway.logger.info('行情服务器登录成功')
            self.gateway.on_login_success()

        else:
            self.gateway.logger.info('行情服务器登录失败')
            self.gateway.send_msg('行情服务器登录失败', isatall=True)

    def onFrontDisconnected(self, reason: int) -> None:
        """服务器连接断开回报"""
        self.login_status = False
        self.gateway.logger.info('行情服务器连接断开')
        self.gateway.send_msg('行情服务器连接断开', isatall=True)

    def close(self) -> None:
        """关闭连接"""
        if self.connect_status:
            self.exit()
        self.gateway.logger.info('行情服务器关闭连接')
        self.gateway.send_msg('行情服务器关闭连接', isatall=True)

    def update_date(self) -> None:
        """更新当前日期"""
        self.current_date = datetime.now().strftime("%Y%m%d")

    def onHeartBeatWarning(self, response):
        self.gateway.logger.info(f'心跳超时警告回调函数,response={response}')
        self.gateway.send_msg(f'心跳超时警告回调函数,response={response}', isatall=True)

    def onRspError(self, error: dict, reqid: int, last: bool) -> None:
        """请求报错回报"""
        self.gateway.logger.info(f'行情接口报错,error={error},reqid={reqid},last={last}')
        self.gateway.send_msg(f'行情接口报错,error={error},reqid={reqid},last={last}', isatall=True)

