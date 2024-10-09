import json
import logging
import random
import os
from datetime import datetime

def setup_logging(log_file='logs/running.log'):
    # 创建日志输出目录（如果不存在）
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # 创建文件处理器并设置级别为 DEBUG
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_list_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"列表文件未找到: {file_path}")
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def save_event_to_file(events, file_path):
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # 创建目录（如果不存在的话）
    
    with open(file_path, 'a') as f:
        #logging.info(f"写入日志: {events}")
        f.write(f"{events}\n")  # 每个日志事件写入一行

            


def get_current_time_format(fmt):
    """
    直接使用配置中的strftime格式，并处理毫秒（如果需要）。
    如果格式包含%f，则截取前3位作为毫秒。
    """
    current_time = datetime.now().strftime(fmt)
    if '%f' in fmt:
        # 查找%f的位置，并截取前3位
        # 假设%f只出现一次
        # 替换%f为前3位微秒
        formatted_time = current_time
        microsecond_str = datetime.now().strftime('%f')
        millisecond_str = microsecond_str[:3]
        formatted_time = formatted_time.replace(microsecond_str, millisecond_str)
        return formatted_time
    else:
        return current_time
