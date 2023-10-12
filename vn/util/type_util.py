import math
import sys
from functools import lru_cache
from typing import Iterable

import numpy


@lru_cache(maxsize=10)
def get_precision_min_value(precision=8) -> float:
    return math.pow(0.1, int(precision))


def convert_to_str(value, default_value=None) -> str:
    return str(value) if value is not None else default_value


def convert_to_int(value, default_value=None) -> int:
    return int(value) if value is not None else default_value


def convert_to_float(value, default_value=None) -> float:
    return float(value) if value is not None else default_value


def get_precision_number(number, precision=8, round_down=False, default=0) -> float:
    if not number:
        return default
    number = float(number)
    if round_down:
        number -= get_precision_min_value(precision) / 2
    return number if precision is None or precision < 0 else round(number, precision)


def valid_inf(value, default=0):
    """ 重置无效值 1.79769313486232e+308 ==> 0 """
    if value is None \
            or value in (numpy.inf, -numpy.inf) \
            or value > sys.maxsize \
            or value == sys.float_info.max:
        value = default
    return value


def get_iter(obj):
    """
    判断是否是可迭代类型，如果不是则转为list
    :param obj: 对象
    :return:    可迭代对象
    """
    if obj is None:
        return []
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, Iterable):
        return list(obj)
    return [obj]






