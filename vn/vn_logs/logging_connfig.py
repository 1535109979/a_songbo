

class LoggingConfig:

    configs = {
        'td': {'file_fp': ''}
    }

import logging

# 创建logger对象
logger = logging.getLogger('my_logger')

# 设置日志级别
logger.setLevel(logging.INFO)

# 创建文件处理器
file_handler = logging.FileHandler('log.txt')

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 添加格式化器到处理器
file_handler.setFormatter(formatter)

# 添加处理器到logger对象
logger.addHandler(file_handler)

# 记录日志
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')

