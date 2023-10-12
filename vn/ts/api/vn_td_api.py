import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional
import logging

import pandas as pd
import pytz
from vnpy_ctp.api import TdApi

from a_songbo.vn.books.account_book import AccountBook
from a_songbo.vn.books.instrument_book import InstrumentBook
from a_songbo.vn.books.position_book import InstrumentPosition
from a_songbo.vn.books.rtn_order import RtnOrder
from a_songbo.vn.books.rtn_trade import RtnTrade
from a_songbo.vn.configs.vn_config import strategy_config
from a_songbo.vn.configs.vn_ctp_constant import PRODUCT_CLASS_CTP2VT, DIRECTION_CTP2VT
from a_songbo.vn.enums.exchange_enum import ExchangeType
from a_songbo.vn.ts.api.constant import *
from a_songbo.vn.util.aio_timer import AioTimer
from a_songbo.vn.util.sys_exception import common_exception
from a_songbo.vn.util.thread import run_in_singleton

if TYPE_CHECKING:
    from a_songbo.vn.ts.vn_trade_gateway import VnTdGateway


class VnCtpTdApi(TdApi):

    def __init__(self, gateway):
        """
        @param gateway: 接口回调处理器
        """
        super().__init__()

        self.gateway: "VnTdGateway" = gateway

        self.logger = None
        self.create_logger()

        self.account_book = AccountBook(account_id=self.gateway.get_configs['account_id'])

        self.userid = self.gateway.get_configs['account_id']
        self.password = self.gateway.get_configs['password']
        self.brokerid = self.gateway.get_configs['brokerid']
        self.auth_code = self.gateway.get_configs['auth_code']
        self.appid = self.gateway.get_configs['appid']
        self.brokerid = self.gateway.get_configs['brokerid']

        # 其他请求id
        self.reqid: int = 0
        # 前置机id
        self.frontid: int = 0
        # 会话id
        self.sessionid: int = 0

        self.order_ref_id: int = 0

        # 报单id映射，用于关联成交回报 { order_ref_id : RtnOrder }
        self.rtn_order_map: Dict[str, RtnOrder] = dict()
        # { order_id: order_ref_id }
        self.order_id_map: Dict[str, str] = dict()

        self.trading_day: Optional[str] = datetime.now().strftime('%Y%m%d')
        self.time_zone = pytz.timezone("Asia/Shanghai")
        self.order_id_pre: Optional[str] = None

        self.inited: bool = False
        self.login_status: bool = False
        self.login_failed: bool = False
        self.ready: bool = False

        # 交易服务器连接状态
        self.connect_status: bool = False
        # 登录状态
        self.login_status: bool = False
        # 授权验证失败
        self.auth_failed: bool = False
        # 授权验证状态
        self.auth_status: bool = False

        self.expire_options = pd.DataFrame(columns=['expire_day', 'exchange', 'left_day'])

        # 添加定时器
        self._add_check_position_timer(interval=30)
        self._add_check_account_timer(interval=97)

    def _add_check_account_timer(self, interval: float):
        """ 定时检查账户资金信息 """

        def _check():
            self._add_check_account_timer(interval)
            self.query_account()

        AioTimer.new_timer(_delay=interval, _func=_check)

    def _add_check_position_timer(self, interval: float):
        """ 定时检查持仓信息 """

        def _check():
            self._add_check_position_timer(interval)
            self.query_position()

            # 没有持仓时无法进入ready状态
            if not self.ready and self.inited and self.login_status and self.connect_status:
                self._set_ready(log_msg=f"positions={len(self.account_book.position_books)}")

        AioTimer.new_timer(_delay=interval, _func=_check)

    def create_logger(self):
        self.logger = logging.getLogger('td_api_log')
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('/Users/edy/byt_pub/a_songbo/vn/vn_logs/td_log.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def connect(self):
        if not self.connect_status:
            path: Path = self.gateway.get_configs['vn_config_home']
            self.createFtdcTraderApi((str(path) + "\\Md").encode("GBK"))

            self.registerFront(self.gateway.get_configs['td_address'])
            self.init()

            time.sleep(2)

    def onFrontConnected(self) -> None:
        """ 当与前置机建立起通信连接时调用。"""
        self.gateway.logger.info("交易服务器连接成功")
        self.connect_status = True

        if self.auth_code:
            self.authenticate()
        else:
            self.login()

    def authenticate(self) -> None:
        """发起授权验证"""
        if self.auth_failed:
            return

        ctp_req: dict = {
            "UserID": self.userid,
            "BrokerID": self.brokerid,
            "AuthCode": self.auth_code,
            "AppID": self.appid
        }

        self.reqid += 1
        self.reqAuthenticate(ctp_req, self.reqid)

    def onRspAuthenticate(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """用户授权验证回报"""
        if not error['ErrorID']:
            self.auth_status = True
            self.gateway.logger.info("交易服务器授权验证成功")
            self.login()
        else:
            self.auth_failed = True
            self.gateway.logger.info("交易服务器授权验证失败", error)
            self.gateway.send_msg(f"交易服务器授权验证失败,error={error}")

    def login(self) -> None:
        """用户登录"""
        if self.login_failed:
            return

        ctp_req: dict = {
            "UserID": self.userid,
            "Password": self.password,
            "BrokerID": self.brokerid,
            "AppID": self.appid
        }

        self.reqid += 1
        self.reqUserLogin(ctp_req, self.reqid)

    def onRspUserLogin(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """用户登录请求回报"""
        if not error["ErrorID"]:
            self.frontid = data["FrontID"]
            self.sessionid = data["SessionID"]
            self.order_id_pre = self._gen_order_id_pre()
            self.login_status = True
            self.gateway.logger.info("交易服务器登录成功")

            # 自动确认结算单
            ctp_req: dict = {
                "BrokerID": self.brokerid,
                "InvestorID": self.userid
            }
            self.reqid += 1
            self.reqSettlementInfoConfirm(ctp_req, self.reqid)
        else:
            self.login_failed = True

            self.gateway.logger.info("交易服务器登录失败", error)
            self.gateway.send_msg(f"交易服务器登录失败,error={error}")

    def onRspSettlementInfoConfirm(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """确认结算单回报"""
        self.gateway.logger.info("结算信息确认成功")

        # 由于流控，单次查询可能失败，通过while循环持续尝试，直到成功发出请求
        while True:
            self.reqid += 1
            n: int = self.reqQryInstrument({}, self.reqid)

            if not n:
                break
            else:
                time.sleep(1)

    def onRspQryInstrument(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """ (self, arg0, arg1, arg2, arg3): 查询合约信息时，当查询结果返回时调用该方法。
        {'reserve1': '', 'ExchangeID': 'CZCE', 'InstrumentName': '纯碱2月', 'reserve2': '', 'reserve3': '', 'ProductClass': '1', 'DeliveryYear': 2024, 'DeliveryMonth': 2, 'MaxMarketOrderVolume': 200, 'MinMarketOrderVolume': 1, 'MaxLimitOrderVolume': 1000, 'MinLimitOrderVolume': 1, 'VolumeMultiple': 20, 'PriceTick': 1.0, 'CreateDate': '20230215', 'OpenDate': '20230215', 'ExpireDate': '20240214', 'StartDelivDate': '20240214', 'EndDelivDate': '20240214', 'InstLifePhase': '1', 'IsTrading': 1, 'PositionType': '2', 'PositionDateType': '2', 'LongMarginRatio': 0.16, 'ShortMarginRatio': 0.16, 'MaxMarginSideAlgorithm': '0', 'reserve4': '', 'StrikePrice': 1.7976931348623157e+308, 'OptionsType': '\x00', 'UnderlyingMultiple': 1.7976931348623157e+308, 'CombinationType': '0', 'InstrumentID': 'SA402', 'ExchangeInstID': 'SA402', 'ProductID': 'SA', 'UnderlyingInstrID': 'SA'}
        """
        product_class: ProductClass = PRODUCT_CLASS_CTP2VT.get(data["ProductClass"])

        self.logger.info(
            "<onRspQryInstrument> reqid=%s last=%s error=%s data=%s %s instrument_books=%s",
            reqid, last, error, data, product_class, len(self.account_book.instrument_books))

        if product_class == ProductClass.FO:
            now = datetime.now()
            target_date = datetime.strptime(data['ExpireDate'], '%Y%m%d')
            time_diff = (target_date - now).days + 1
            if (time_diff > strategy_config['expire_day_left_period'][0] < time_diff
                    <= strategy_config['expire_day_left_period'][1]):
                self.expire_options.loc[data['InstrumentName']] = [data['ExpireDate'], data['ExchangeID'], time_diff]

        if product_class:
            data["product_class"] = product_class

            # 更新合约属性字典
            book: InstrumentBook = self.account_book.get_instrument_book(
                vt_symbol=f'{data["InstrumentID"]}.{data["ExchangeID"]}')
            book.update_data(data=data)

        # 初始化成功
        if last and not self.inited:
            self.gateway.logger.info("合约信息查询成功")

            self.expire_options['datetime'] = datetime.now()
            self.expire_options.index.name = 'code'
            self.expire_options = self.expire_options.reset_index()
            self.expire_options.to_csv('/Users/edy/byt_pub/a_songbo/vn/data/expire_options.csv')

            self._set_inited(log_msg="instrument_books={}".format(
                len(self.account_book.instrument_books)))

    def _set_inited(self, log_msg: str, inited: bool = True):
        self.inited = inited
        self.gateway.logger.info(f"<inited> {log_msg}")

        self.query_account()

    def query_account(self):
        if not self.connect_status or not self.login_status or not self.inited:
            self.gateway.logger.info(
                f"当前状态不能发起请求! connect:{self.connect_status} login:{self.login_status} inited:{self.inited}")
            return -1

        req: dict = {
            "BrokerID": self.brokerid,
            "InvestorID": self.userid,
        }
        self.reqid += 1
        self.gateway.logger.info(f"<reqQryTradingAccount> reqid={self.reqid} req={req}")
        self.reqQryTradingAccount(req, self.reqid)

    def onRspQryTradingAccount(self, data: dict, error: dict, reqid: int, last: bool) -> None:
        """ 查询资金账户响应
        {'BrokerID': '9999', 'AccountID': '146591', 'PreMortgage': 0.0, 'PreCredit': 0.0, 'PreDeposit': 62000000.0, 'PreBalance': 62000000.0, 'PreMargin': 0.0, 'InterestBase': 0.0, 'Interest': 0.0, 'Deposit': 0.0, 'Withdraw': 0.0, 'FrozenMargin': 0.0, 'FrozenCash': 0.0, 'FrozenCommission': 0.0, 'CurrMargin': 8654943.6, 'CashIn': 0.0, 'Commission': 2710.714660018958, 'CloseProfit': 7500.0, 'PositionProfit': -62585.0, 'Balance': 61942204.28533998, 'Available': 53287260.68533998, 'WithdrawQuota': 42623808.548271984, 'Reserve': 0.0, 'TradingDay': '20230608', 'SettlementID': 1, 'Credit': 0.0, 'Mortgage': 0.0, 'ExchangeMargin': 8654943.6, 'DeliveryMargin': 0.0, 'ExchangeDeliveryMargin': 0.0, 'ReserveBalance': 0.0, 'CurrencyID': 'CNY', 'PreFundMortgageIn': 0.0, 'PreFundMortgageOut': 0.0, 'FundMortgageIn': 0.0, 'FundMortgageOut': 0.0, 'FundMortgageAvailable': 0.0, 'MortgageableFund': 53279760.68533998, 'SpecProductMargin': 0.0, 'SpecProductFrozenMargin': 0.0, 'SpecProductCommission': 0.0, 'SpecProductFrozenCommission': 0.0, 'SpecProductPositionProfit': 0.0, 'SpecProductCloseProfit': 0.0, 'SpecProductPositionProfitByAlg': 0.0, 'SpecProductExchangeMargin': 0.0, 'BizType': '\\x00', 'FrozenSwap': 0.0, 'RemainSwap': 0.0}
        """
        self.logger.info(
            f"<onRspQryTradingAccount> reqid={reqid} last={last} error={error} data={data}")

        # 更新账户信息字典
        old_avail = self.account_book.avail
        self.account_book.update_data(data=data)

        if last and not self.ready:
            self.query_position()

    def query_position(self, exchange_type: str = None, instrument: str = None) -> int:
        """ 请求查询投资者持仓 """
        if not self.connect_status or not self.login_status or not self.inited:
            self.gateway.logger.info(
                f"当前状态不能发起请求! connect:{self.connect_status} login:{self.login_status} inited:{self.inited}")
            return -1

        req: dict = {
            "BrokerID": self.brokerid,
            "InvestorID": self.userid,
        }
        if exchange_type:
            req["ExchangeID"] = str(exchange_type)
        if instrument:
            req["InstrumentID"] = instrument
        self.reqid += 1
        self.gateway.logger.info(f"<reqQryInvestorPosition> reqid={self.reqid} req={req}")

        result = self.reqQryInvestorPosition(req, self.reqid)
        return result

    def onRspQryInvestorPosition(self, data: dict, error: dict, reqid: int, last: bool):
        """ (self, arg0: dict, arg1: dict, arg2: int, arg3: bool) -> None 查询持仓响应，返回查询结果。
        {'reserve1': 'ag2308', 'BrokerID': '9999', 'InvestorID': '146591', 'PosiDirection': '3', 'HedgeFlag': '1', 'PositionDate': '1', 'YdPosition': 0, 'Position': 22, 'LongFrozen': 0, 'ShortFrozen': 0, 'LongFrozenAmount': 0.0, 'ShortFrozenAmount': 0.0, 'OpenVolume': 22, 'CloseVolume': 0, 'OpenAmount': 1826880.0, 'CloseAmount': 0.0, 'PositionCost': 1826880.0, 'PreMargin': 0.0, 'UseMargin': 347107.19999999995, 'FrozenMargin': 0.0, 'FrozenCash': 0.0, 'FrozenCommission': 0.0, 'CashIn': 0.0, 'Commission': 18.29080000174344, 'CloseProfit': 0.0, 'PositionProfit': 1320.0, 'PreSettlementPrice': 5646.0, 'SettlementPrice': 5532.0, 'TradingDay': '20230615', 'SettlementID': 1, 'OpenCost': 1826880.0, 'ExchangeMargin': 347107.19999999995, 'CombPosition': 0, 'CombLongFrozen': 0, 'CombShortFrozen': 0, 'CloseProfitByDate': 0.0, 'CloseProfitByTrade': 0.0, 'TodayPosition': 22, 'MarginRateByMoney': 0.19, 'MarginRateByVolume': 0.0, 'StrikeFrozen': 0, 'StrikeFrozenAmount': 0.0, 'AbandonFrozen': 0, 'ExchangeID': 'SHFE', 'YdStrikeFrozen': 0, 'InvestUnitID': '', 'PositionCostOffset': 0.0, 'TasPosition': 0, 'TasPositionCost': 0.0, 'InstrumentID': 'ag2308'}
        """
        self.logger.info(f"<onRspQryInvestorPosition> "
                         f"reqid={reqid} last={last} error={error} data={data}")
        self.__onRspQryInvestorPosition__(data, error, reqid, last)

    @run_in_singleton
    def __onRspQryInvestorPosition__(self, data: dict, error: dict, reqid: int, last: bool):
        if data and (not error or not error.get("ErrorID")):
            data["reqid"] = reqid

            position: InstrumentPosition = self.account_book.get_instrument_position(
                vt_symbol=f'{data["InstrumentID"]}.{data["ExchangeID"]}',
                direction=DIRECTION_CTP2VT[data["PosiDirection"]])
            position.append_data(data=data)

        if last:
            for vt_symbol, book in self.account_book.position_books.items():
                instrument_book: InstrumentBook = self.account_book.get_instrument_book(vt_symbol)

                for position in (book.long_position, book.short_position):
                    old_volume = position.volume
                    old_open_avg = position.open_avg

                    if position.update_by_datas(instrument_book=instrument_book, reqid=reqid):
                        if not self.ready or position.volume:
                            self.gateway.logger.info(f"<position> reqid={reqid} {position}")

                        if self.ready and (position.volume != old_volume or
                                           position.open_avg != old_open_avg):
                            error_msg = f"持仓信息不一致，已校正 !!! reqid={reqid} " \
                                        f"{book.instrument} {position.direction.value} " \
                                        f"volume: {old_volume} ==> {position.volume} " \
                                        f"open_avg: {old_open_avg} ==> {position.open_avg}"
                            # self.gateway.send_position_error_msg(
                            #     instrument=book.instrument, error_old=error_msg)
                            self.gateway.on_account_update()
            if not self.ready:
                self.__reqQryInvestorPositionDetail__()

    @common_exception(log_flag=True)
    def __reqQryInvestorPositionDetail__(
            self, exchange_type: ExchangeType = None, instrument: str = None) -> int:
        """ 请求查询投资者持仓明细 """
        if not self.connect_status or not self.login_status or not self.inited:
            self.gateway.logger.warning(
                "当前状态不能发起请求! connect:%s login:%s inited:%s",
                self.connect_status, self.login_status, self.inited)
            return -1
        req: dict = {
            "BrokerID": self.brokerid,
            "InvestorID": self.userid,
        }
        if exchange_type:
            req["ExchangeID"] = str(exchange_type)
        if instrument:
            req["InstrumentID"] = instrument
        self.reqid += 1
        self.gateway.logger.info("<reqQryInvestorPositionDetail> reqid=%s req=%s",
                                 self.reqid, req)

        result = self.reqQryInvestorPositionDetail(req, self.reqid)
        assert not result, f"reqQryInvestorPositionDetail error:{result}"
        return result

    @common_exception()
    def onRspQryInvestorPositionDetail(self, data: dict, error: dict, reqid: int, last: bool):
        """ 投资者持仓明细查询响应
        {'reserve1': 'ag2308', 'BrokerID': '9999', 'InvestorID': '146591', 'HedgeFlag': '1', 'Direction': '1', 'OpenDate': '20230615', 'TradeID': '          30', 'Volume': 22, 'OpenPrice': 5536.0, 'TradingDay': '20230615', 'SettlementID': 1, 'TradeType': '0', 'reserve2': '', 'ExchangeID': 'SHFE', 'CloseProfitByDate': 0.0, 'CloseProfitByTrade': 0.0, 'PositionProfitByDate': 0.0, 'PositionProfitByTrade': 0.0, 'Margin': 347107.19999999995, 'ExchMargin': 347107.19999999995, 'MarginRateByMoney': 0.19, 'MarginRateByVolume': 0.0, 'LastSettlementPrice': 5646.0, 'SettlementPrice': 5536.0, 'CloseVolume': 0, 'CloseAmount': 0.0, 'TimeFirstVolume': 0, 'InvestUnitID': '', 'SpecPosiType': '#', 'InstrumentID': 'ag2308', 'CombInstrumentID': ''}
        """
        self.__onRspQryInvestorPositionDetail__(data, error, reqid, last)

    @run_in_singleton
    def __onRspQryInvestorPositionDetail__(
            self, data: dict, error: dict, reqid: int, last: bool):
        self.logger.info(f"<onRspQryInvestorPositionDetail> "
                         f"reqid={reqid} last={last} error={error} data={data}")

        if data and (not error or not error.get("ErrorID")):
            data["reqid"] = reqid

            position: InstrumentPosition = self.account_book.get_instrument_position(
                vt_symbol=f'{data["InstrumentID"]}.{data["ExchangeID"]}',
                direction=DIRECTION_CTP2VT[data["Direction"]])
            position.append_detail(data=data)

        if last:
            for vt_symbol, book in self.account_book.position_books.items():
                instrument_book: InstrumentBook = self.account_book.get_instrument_book(
                    vt_symbol=vt_symbol)

                for position in (book.long_position, book.short_position):
                    old_avg = position.avg
                    old_cost = position.cost

                    if position.update_by_details(instrument_book=instrument_book, reqid=reqid):
                        if not self.ready or position.volume:
                            self.gateway.logger.info(f"<position> reqid={reqid} {position}")

            # 设置状态为已就绪
            if not self.ready:
                self._set_ready(log_msg=f"positions={len(self.account_book.position_books)}")

    def _set_ready(self, log_msg: str, ready: bool = True):
        self.ready = ready
        self.gateway.logger.info("<ready> %s", log_msg)
        self.gateway.send_msg('交易服务启动成功')

    def _gen_order_id_pre(self) -> str:
        """ 拼接委托id前缀: 721011010961007 """
        return f"{str(self.trading_day)[-3:]}{str(self.frontid).zfill(2)}" \
               f"{str(self.sessionid).replace('-', '0').zfill(10)}"

    def _gen_order_id(self, order_ref_id) -> str:
        """ 拼接委托id: 721011010961007000000001 """
        return f"{self.order_id_pre}{str(order_ref_id).zfill(9)}"

    def insert_order(self, instrument: str, exchange_type: ExchangeType,
                     volume: int, price: float, order_price_type: OrderPriceType,
                     offset_flag: OffsetFlag, direction: Direction) -> str:
        """ 委托下单 """
        if not self.connect_status or not self.login_status or not self.inited \
                or not self.ready:
            self.gateway.logger.warning(
                "当前状态不能发起请求! connect:%s login:%s inited:%s ready:%s",
                self.connect_status, self.login_status, self.inited, self.ready)
            return "0"

        self.order_ref_id += 1
        order_ref_id = str(self.order_ref_id)
        order_id: str = self._gen_order_id(order_ref_id)
        price_type, time_condition, volume_condition = ORDER_PRICE_TYPE_VT2CTP[order_price_type]

        req: dict = {
            "BrokerID": self.brokerid, "InvestorID": self.userid,
            "MinVolume": 1, "IsAutoSuspend": 0,
            "CombHedgeFlag": THOST_FTDC_HF_Speculation,
            "ContingentCondition": THOST_FTDC_CC_Immediately,
            "ForceCloseReason": THOST_FTDC_FCC_NotForceClose,
            "CombOffsetFlag": OFFSET_FLAG_VT2CTP[offset_flag],
            "Direction": DIRECTION_VT2CTP[direction],
            "TimeCondition": time_condition, "VolumeCondition": volume_condition,
            "OrderPriceType": price_type, "LimitPrice": price, "VolumeTotalOriginal": volume,
            "ExchangeID": str(exchange_type), "InstrumentID": instrument,
            "OrderRef": order_ref_id
        }

        self.reqid += 1
        self.gateway.logger.info(
            "<reqOrderInsert> reqid=%s req=%s order_id=%s", self.reqid, req, order_id)

        result: int = self.reqOrderInsert(req, self.reqid)
        assert not result, f"reqOrderInsert error:{result}"

        # 关联报单id
        self.order_id_map[order_id] = order_ref_id

        # 创建一个初始化的下单回报对象
        req["front_id"] = self.frontid
        req["session_id"] = self.sessionid

        rtn = RtnOrder.create_by_insert_req(data=req, order_id=order_id, trading_day=self.trading_day,)
        self.rtn_order_map[order_ref_id] = rtn

        return order_id

    def onRtnOrder(self, data: dict) -> None:
        """ (self, arg0: dict) -> None: 报单通知
        {'BrokerID': '9999', 'InvestorID': '146591', 'reserve1': 'ag2309', 'OrderRef': '350402519040', 'UserID': '146591', 'OrderPriceType': '2', 'Direction': '0', 'CombOffsetFlag': '0', 'CombHedgeFlag': '1', 'LimitPrice': 5645.0, 'VolumeTotalOriginal': 10, 'TimeCondition': '1', 'GTDDate': '', 'VolumeCondition': '1', 'MinVolume': 1, 'ContingentCondition': '1', 'StopPrice': 0.0, 'ForceCloseReason': '0', 'IsAutoSuspend': 0, 'BusinessUnit': '9999cac', 'RequestID': 0, 'OrderLocalID': '        2338', 'ExchangeID': 'SHFE', 'ParticipantID': '9999', 'ClientID': '9999146571', 'reserve2': 'ag2309', 'TraderID': '9999cac', 'InstallID': 1, 'OrderSubmitStatus': '0', 'NotifySequence': 0, 'TradingDay': '20230616', 'SettlementID': 1, 'OrderSysID': '', 'OrderSource': '0', 'OrderStatus': 'a', 'OrderType': '0', 'VolumeTraded': 0, 'VolumeTotal': 10, 'InsertDate': '20230619', 'InsertTime': '20:55:41', 'ActiveTime': '', 'SuspendTime': '', 'UpdateTime': '', 'CancelTime': '', 'ActiveTraderID': '', 'ClearingPartID': '', 'SequenceNo': 0, 'FrontID': 1, 'SessionID': 1341667273, 'UserProductInfo': 'GD', 'StatusMsg': '报单已提交', 'UserForceClose': 0, 'ActiveUserID': '', 'BrokerOrderSeq': 9983, 'RelativeOrderSysID': '', 'ZCETotalTradedVolume': 0, 'IsSwapOrder': 0, 'BranchID': '', 'InvestUnitID': '', 'AccountID': '', 'CurrencyID': '', 'reserve3': '', 'MacAddress': '', 'InstrumentID': 'ag2309', 'ExchangeInstID': 'ag2309', 'IPAddress': ''}
        {'BrokerID': '9999', 'InvestorID': '146591', 'reserve1': 'ag2309', 'OrderRef': '350402519040', 'UserID': '146591', 'OrderPriceType': '2', 'Direction': '0', 'CombOffsetFlag': '0', 'CombHedgeFlag': '1', 'LimitPrice': 5645.0, 'VolumeTotalOriginal': 10, 'TimeCondition': '1', 'GTDDate': '', 'VolumeCondition': '1', 'MinVolume': 1, 'ContingentCondition': '1', 'StopPrice': 0.0, 'ForceCloseReason': '0', 'IsAutoSuspend': 0, 'BusinessUnit': '9999cac', 'RequestID': 0, 'OrderLocalID': '        2338', 'ExchangeID': 'SHFE', 'ParticipantID': '9999', 'ClientID': '9999146571', 'reserve2': 'ag2309', 'TraderID': '9999cac', 'InstallID': 1, 'OrderSubmitStatus': '0', 'NotifySequence': 0, 'TradingDay': '20230616', 'SettlementID': 1, 'OrderSysID': '        7919', 'OrderSource': '0', 'OrderStatus': 'a', 'OrderType': '0', 'VolumeTraded': 0, 'VolumeTotal': 10, 'InsertDate': '20230615', 'InsertTime': '20:55:41', 'ActiveTime': '', 'SuspendTime': '', 'UpdateTime': '', 'CancelTime': '', 'ActiveTraderID': '9999cac', 'ClearingPartID': '', 'SequenceNo': 3400, 'FrontID': 1, 'SessionID': 1341667273, 'UserProductInfo': 'GD', 'StatusMsg': '报单已提交', 'UserForceClose': 0, 'ActiveUserID': '', 'BrokerOrderSeq': 9983, 'RelativeOrderSysID': '', 'ZCETotalTradedVolume': 0, 'IsSwapOrder': 0, 'BranchID': '', 'InvestUnitID': '', 'AccountID': '', 'CurrencyID': '', 'reserve3': '', 'MacAddress': '', 'InstrumentID': 'ag2309', 'ExchangeInstID': 'ag2309', 'IPAddress': ''}
        {'BrokerID': '9999', 'InvestorID': '146591', 'reserve1': 'ag2309', 'OrderRef': '350402519040', 'UserID': '146591', 'OrderPriceType': '2', 'Direction': '0', 'CombOffsetFlag': '0', 'CombHedgeFlag': '1', 'LimitPrice': 5645.0, 'VolumeTotalOriginal': 10, 'TimeCondition': '1', 'GTDDate': '', 'VolumeCondition': '1', 'MinVolume': 1, 'ContingentCondition': '1', 'StopPrice': 0.0, 'ForceCloseReason': '0', 'IsAutoSuspend': 0, 'BusinessUnit': '9999cac', 'RequestID': 0, 'OrderLocalID': '        2338', 'ExchangeID': 'SHFE', 'ParticipantID': '9999', 'ClientID': '9999146571', 'reserve2': 'ag2309', 'TraderID': '9999cac', 'InstallID': 1, 'OrderSubmitStatus': '0', 'NotifySequence': 0, 'TradingDay': '20230616', 'SettlementID': 1, 'OrderSysID': '        7919', 'OrderSource': '0', 'OrderStatus': '0', 'OrderType': '0', 'VolumeTraded': 10, 'VolumeTotal': 0, 'InsertDate': '20230615', 'InsertTime': '20:55:41', 'ActiveTime': '', 'SuspendTime': '', 'UpdateTime': '', 'CancelTime': '', 'ActiveTraderID': '9999cac', 'ClearingPartID': '', 'SequenceNo': 3400, 'FrontID': 1, 'SessionID': 1341667273, 'UserProductInfo': 'GD', 'StatusMsg': '全部成交报单已提交', 'UserForceClose': 0, 'ActiveUserID': '', 'BrokerOrderSeq': 9983, 'RelativeOrderSysID': '', 'ZCETotalTradedVolume': 0, 'IsSwapOrder': 0, 'BranchID': '', 'InvestUnitID': '', 'AccountID': '', 'CurrencyID': '', 'reserve3': '', 'MacAddress': '', 'InstrumentID': 'ag2309', 'ExchangeInstID': 'ag2309', 'IPAddress': ''}
        """

        self.__onRtnOrder__(data)

    @run_in_singleton
    @common_exception()
    def __onRtnOrder__(self, data: dict):
        rtn: RtnOrder = self.rtn_order_map.get(data["OrderRef"])
        if rtn and self.order_id_map.__contains__(rtn.order_id):
            self.gateway.logger.info(f"<onRtnOrder> order_id={rtn.order_id} data={data}")

            rtn.update_by_rtn_data(data=data, timezone=self.time_zone)

            # self.gateway.on_order(rtn.data)

    def onRtnTrade(self, data: dict) -> None:
        """ (self, arg0: dict) -> None: 成交通知
        {'BrokerID': '9999', 'InvestorID': '146591', 'reserve1': 'ag2309', 'OrderRef': '350402519040', 'UserID': '146591', 'ExchangeID': 'SHFE', 'TradeID': '        6903', 'Direction': '0', 'OrderSysID': '        7919', 'ParticipantID': '9999', 'ClientID': '9999146571', 'TradingRole': '\\x00', 'reserve2': 'ag2309', 'OffsetFlag': '0', 'HedgeFlag': '1', 'Price': 5623.0, 'Volume': 10, 'TradeDate': '20230615', 'TradeTime': '20:55:41', 'TradeType': '\\x00', 'PriceSource': '\\x00', 'TraderID': '9999cac', 'OrderLocalID': '        2338', 'ClearingPartID': '9999', 'BusinessUnit': '', 'SequenceNo': 3401, 'TradingDay': '20230616', 'SettlementID': 1, 'BrokerOrderSeq': 9983, 'TradeSource': '0', 'InvestUnitID': '', 'InstrumentID': 'ag2309', 'ExchangeInstID': 'ag2309'}
        {'BrokerID': '9999', 'InvestorID': '146591', 'reserve1': 'ag2309', 'OrderRef': '112', 'UserID': '146591', 'ExchangeID': 'SHFE', 'TradeID': '        7239', 'Direction': '1', 'OrderSysID': '        8655', 'ParticipantID': '9999', 'ClientID': '9999146571', 'TradingRole': '\\x00', 'reserve2': 'ag2309', 'OffsetFlag': '3', 'HedgeFlag': '1', 'Price': 5621.0, 'Volume': 2, 'TradeDate': '20230615', 'TradeTime': '21:53:47', 'TradeType': '\\x00', 'PriceSource': '\\x00', 'TraderID': '9999cac', 'OrderLocalID': '        2988', 'ClearingPartID': '9999', 'BusinessUnit': '', 'SequenceNo': 4073, 'TradingDay': '20230616', 'SettlementID': 1, 'BrokerOrderSeq': 11016, 'TradeSource': '0', 'InvestUnitID': '', 'InstrumentID': 'ag2309', 'ExchangeInstID': 'ag2309'}
        """
        self.__onRtnTrade__(data)

    @run_in_singleton
    @common_exception()
    def __onRtnTrade__(self, data: dict):
        rtn_order: RtnOrder = self.rtn_order_map.get(data["OrderRef"])
        if rtn_order and self.order_id_map.__contains__(rtn_order.order_id):
            self.gateway.logger.info(f"<onRtnTrade> order_id={rtn_order.order_id} data={data}")
            rtn_trade: RtnTrade = RtnTrade.create_by_rtn_data(
                data=data, rtn_order=rtn_order, timezone=self.time_zone)
            position: InstrumentPosition = self.account_book.update_by_trade_rtn(
                rtn=rtn_trade)
            self.gateway.logger.info(
                f"<update_by_trade_rtn> {position.direction.value} "
                f"{rtn_trade.offset_flag.name}"
                f"order_id:{rtn_trade.order_id} trade_id:{rtn_trade.trade_id} "
                f"avail:{self.account_book.avail} {position}")
            self.gateway.on_trade(rtn_trade.data)

        if self.ready:
            self.query_position()

    def onRspError(self, error: dict, reqid: int, last: bool) -> None:
        """ (arg0: dict, arg1: int, arg2: bool) -> None：错误应答时调用。"""
        self.gateway.logger.error(f"<onRspError> reqid={reqid} last={last} error={error}")

        error["reqid"] = reqid
        self.gateway.on_error(error)

    def onHeartBeatWarning(self, reqid: int) -> None:
        """ 心跳超时警告 """
        self.gateway.logger.warning(f"<onHeartBeatWarning> reqid={reqid}")

    @common_exception()
    def close(self) -> None:
        """关闭连接"""
        try:
            if self.connect_status:
                self.gateway.logger.info(f'<td close>')
                # exit(self) -> int：退出交易接口。
                self.exit()

                # join(self) -> int：等待交易接口线程退出。
                self.join()
        except Exception as e:
            self.gateway.logger.error(f'<td close> error {e}')
