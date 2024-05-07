# example.py
import time

import sys
import logging


# 加载代码的时候就创建根日志对象对象, 防止被第三方库先创建
root_logger = logging.getLogger()
root_logger.addHandler(logging.StreamHandler(stream=sys.stdout))
root_logger.setLevel(logging.DEBUG)


# # 配置日志输出到文件
#  logging.basicConfig()
# root_logger.addHandler(root_handler)
# filename='/Users/edy/byt_pub/a_songbo/vedio_study/superciosor_demo/example.log', level=logging.INFO
# # 重定向 sys.stdout 和 sys.stderr 到日志
# sys.stdout = sys.stderr = open('/Users/edy/byt_pub/a_songbo/vedio_study/superciosor_demo/example.log', 'a')
#
# # 此后的 print 语句将输出到日志文件
# print('Hello, this will be logged.')


while True:
    # print("Hello, Supervisor!")
    root_logger.info('Hello, Supervisor!')
    time.sleep(5)
