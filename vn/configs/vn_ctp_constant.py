from typing import Dict

from a_songbo.vn.enums.exchange_enum import ProductClass, Direction

THOST_FTDC_PC_Futures = '1'
THOST_FTDC_PC_Options = '2'
THOST_FTDC_D_Buy = '0'
THOST_FTDC_D_Sell = '1'
THOST_FTDC_PD_Long = '2'
THOST_FTDC_PD_Short = '3'


# 多空方向映射
DIRECTION_VT2CTP: Dict[Direction, str] = {
    Direction.LONG: THOST_FTDC_D_Buy,
    Direction.SHORT: THOST_FTDC_D_Sell
}
DIRECTION_CTP2VT: Dict[str, Direction] = {v: k for k, v in DIRECTION_VT2CTP.items()}
DIRECTION_CTP2VT[THOST_FTDC_PD_Long] = Direction.LONG
DIRECTION_CTP2VT[THOST_FTDC_PD_Short] = Direction.SHORT

# 产品类型映射
PRODUCT_CLASS_VT2CTP: Dict[ProductClass, str] = {
    ProductClass.F: THOST_FTDC_PC_Futures,
    ProductClass.FO: THOST_FTDC_PC_Options,
}
PRODUCT_CLASS_CTP2VT: Dict[str, ProductClass] = {v: k for k, v in PRODUCT_CLASS_VT2CTP.items()}


