#!/usr/bin/env python
import logging
import time

from binance.um_futures import UMFutures


key = "8kHJ8xMwb8wZkrTy17IVOym4CDo5qS6JFP8suvpsDaWCqjuBuIAn29HFYKuQM1bE"
secret = "uUH1X2sz5jnMVhL44zxHiphnxhoQ5swPs62gFg4JFLCRayWwFr2MZJm9dJlaM2WK"

# key = "R8cR2rb6822fDtpdL7nFX9fNsoC8WdaNfK4K38C8vQrbsHuuE8WmSne0t29gRsN8"
# secret = "eHTwScKu61eYJSwzEe6tHcyavKOfROino1jncIuQnE8beMh4ljRXcXJD0Uzuadcj"

hmac_client = UMFutures(key=key, secret=secret)
data = hmac_client.account()

print(data['totalCrossWalletBalance'])

