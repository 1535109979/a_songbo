import logging

logging.basicConfig(filename='mylogsdemo.log', level=logging.DEBUG,
                    format='%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')


def funcv():

    logging.info('dfgdsfg')

    try:
        # 程序代码
        1 / 0
    except Exception as e:
        # 报错时写入日志
        logging.error(f"出现错误：{str(e)}", exc_info=True)


funcv()
