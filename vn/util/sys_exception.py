import functools
import logging
import traceback

from a_songbo.vn.util.dingding import Dingding

logger = logging.getLogger('common_exception_log')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('/Users/edy/byt_pub/a_songbo/vn/vn_logs/common_exception.log')
formatter = logging.Formatter('%(asctime)s %(module)s %(funcName)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def common_exception(log_flag: bool = None):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                traceback.print_exc()
                log_msg = "!!!error= %s !!! %s" % (e, kwargs)
                logger.exception(log_msg)
                if log_flag:
                    logger.info(log_msg)
                    Dingding.send_msg(log_msg, isatall=True)

        return wrapper

    return decorator


# try:
#     # 执行可能引发异常的代码
#     result = 1 / 0
# except Exception as e:
#     # 记录异常信息
#     # logger.exception("An exception occurred")
#     logger.info(e)
