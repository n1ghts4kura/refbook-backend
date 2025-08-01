# logging.py
# 简单的日志输出模块
#

import logging
import sys

# 创建logger
logger = logging.getLogger("refbook")
logger.setLevel(logging.DEBUG)

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# 创建格式化器
formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
console_handler.setFormatter(formatter)

# 添加处理器到logger
logger.addHandler(console_handler)

def info(message: str):
    """输出信息日志"""
    logger.info(message)

def debug(message: str):
    """输出调试日志"""
    logger.debug(message)

def warning(message: str):
    """输出警告日志"""
    logger.warning(message)

def error(message: str):
    """输出错误日志"""
    logger.error(message)
