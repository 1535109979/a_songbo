
from enum import unique

from a_songbo.vn.enums.exchange_enum import BaseEnum


@unique
class ResultCodeMsg(BaseEnum):
    SUCCESS = (0, "success")
    EXCEPTION = (2, "Exception: %s")
    CLIENT_EXCEPTION = (4, "Client Exception: %s")
    SERVER_EXCEPTION = (5, "Server Exception: %s")
    CLOCK_MOVING_EXCEPTION = (6, "Clock Moving Exception: %s")

    # 报单异常
    BALANCE_INSUFFICIENT = (10, "balance insufficient: %s")
    EXCHANGE_EXCEPTION = (15, "exchange exception: %s")

    # 签名
    BAD_SIGNATURE = (100, "invalid signature")
    EXPIRED_SIGNATURE = (101, "expired signature")

    # 参数
    REQUIRED_PARAS = (1000, "%s is required")
    INCORRECT_PARAS = (1001, "%s is incorrect")
    NO_DATA = (1002, "%s no data")
    ALREADY_EXISTS = (1003, "%s already exists")
    NOT_EXIST = (1004, "%s not exist")
    NOT_AVAILABLE = (1005, "%s not available")

    def get_code(self):
        return self.value[0]

    def get_msg(self):
        return self.value[1]

    def get_format_msg(self, *args):
        msg = self.get_msg()
        if args:
            msg = msg % args
        return "code={},msg={}".format(self.get_code(), msg)


@unique
class AppType(BaseEnum):
    """自定义应用类型"""
    SCRIPT = "script"
    STRATEGY = "strategy"
    BACKTEST = "backtest"
    SCHEDULE = "schedule"
    WEB_SERVER = "web_server"

    @staticmethod
    def get_app_type_values():
        return [s.value for s in AppType.__members__.values()]


@unique
class EngineNameMode(BaseEnum):
    ACCOUNT = "a"
    USER = "u"
