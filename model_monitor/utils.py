import os
import logging
from datetime import datetime

# def setup_logger(log_dir: str) -> logging.Logger:
#     """设置日志系统"""
#     # 创建日志目录
#     if not os.path.exists(log_dir):
#         os.makedirs(log_dir)
    
#     # 按日期创建子文件夹
#     date_str = datetime.now().strftime('%Y%m%d')
#     daily_log_dir = os.path.join(log_dir, date_str)
#     if not os.path.exists(daily_log_dir):
#         os.makedirs(daily_log_dir)
    
#     # 创建唯一日志文件名
#     timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#     log_filename = f"monitor_{timestamp}.log"
#     log_path = os.path.join(daily_log_dir, log_filename)
    
#     # 配置日志
#     logger = logging.getLogger('model_monitor')
#     logger.setLevel(logging.INFO)
    
#     # 清除已有Handler
#     if logger.hasHandlers():
#         logger.handlers.clear()
    
#     # 添加文件Handler
#     file_handler = logging.FileHandler(log_path, encoding='utf-8')
#     file_formatter = logging.Formatter(
#         '%(asctime)s - %(levelname)s - %(message)s',
#         datefmt='%Y-%m-%d %H:%M:%S'
#     )
#     file_handler.setFormatter(file_formatter)
#     logger.addHandler(file_handler)
    
#     # 添加控制台Handler
#     console_handler = logging.StreamHandler()
#     console_formatter = logging.Formatter(
#         '%(asctime)s - %(levelname)s - %(message)s',
#         datefmt='%Y-%m-%d %H:%M:%S'
#     )
#     console_handler.setFormatter(console_formatter)
#     logger.addHandler(console_handler)
    
#     logger.info(f"日志文件路径: {log_path}")
#     return logger
# utils.py


def setup_logger(log_dir: str) -> logging.Logger:
    """配置 root 日志器，确保所有日志（包括第三方库）都写入文件"""
    # 1. 获取 root 日志器（Python 所有日志的根节点）
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # 捕获 INFO 及以上级别日志

    # 2. 清除已有 Handler（避免重复输出）
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # 3. 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    date_str = datetime.now().strftime('%Y%m%d')
    daily_log_dir = os.path.join(log_dir, date_str)
    os.makedirs(daily_log_dir, exist_ok=True)

    # 4. 日志文件路径
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    log_path = os.path.join(daily_log_dir, f"monitor_{timestamp}.log")

    # 5. 添加文件 Handler（写入日志文件）
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 包含日志器名称（如 root、yagmail）
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # 6. 添加控制台 Handler（同时输出到控制台）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(file_formatter)
    root_logger.addHandler(console_handler)

    root_logger.info(f"root 日志器初始化完成，日志文件路径: {log_path}")
    return root_logger
