import logging
from logging.handlers import TimedRotatingFileHandler
import os

# 创建日志目录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 设置日志文件名，例如：app.log.2024-08-13
log_file = os.path.join(log_dir, "app.log")

# 创建日志记录器
logger = logging.getLogger("MyLogger")
logger.setLevel(logging.INFO)  # 设置日志级别

# 创建一个TimedRotatingFileHandler，每天滚动日志
handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
handler.suffix = "%Y-%m-%d.log"  # 设置滚动后文件的后缀
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# 将handler添加到日志记录器
logger.addHandler(handler)

# 测试日志
logger.info("This is an info message")
