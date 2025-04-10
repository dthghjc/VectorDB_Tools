import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
LOG_FILENAME = 'system.log'

# 确保日志目录存在
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file_path = os.path.join(LOG_DIR, LOG_FILENAME)

def setup_logging():
    """Configures the root logger for the application."""
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器(循环)
    # 当日志达到10MB时进行循环,保留5个备份日志
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO) # 将INFO及以上级别的日志写入文件
    
    # 控制台处理器(可选,用于开发时在控制台查看日志)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG) # 将DEBUG及以上级别的日志输出到控制台

    # 获取根日志记录器并配置
    root_logger = logging.getLogger()
    # 设置最低捕获级别(控制台为DEBUG,文件为INFO)
    root_logger.setLevel(logging.DEBUG) 
    
    # 避免多次调用setup_logging时重复添加处理器
    if not root_logger.handlers:
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        root_logger.info("Logging configured: File handler added.")
    else:
        # 如果处理器已存在,可以更新级别或检查配置
        # 为简单起见,假设setup只在启动时调用一次
        pass

# 是否在导入此模块时自动调用setup?
# 注意多次导入可能会重复调用
# setup_logging()

# 用于在其他模块中获取日志记录器实例的函数
def get_logger(name):
    """Gets a logger instance with the specified name."""
    return logging.getLogger(name) 