import re
import time
import random
import os
from .config import Config
from .utils import load_list_file, get_current_time_format, save_event_to_file
import logging
from datetime import datetime
import configparser

class LogSimulator:
    def __init__(self, template_path, config_path, output_path, rate_config=None, trading_days_file=None, stress_test=False ,stress_rate = None):
        self.template = self._load_template(template_path)
        self.config = Config(config_path).get_tokens()
        self.output_path = output_path
        self.rate_config_path = rate_config  # Path to rate_config.ini
        self.trading_days_file = trading_days_file  # Path to trading days list

        self.stress_test = stress_test  # 压力测试模式标志
        self.stress_rate = stress_rate

        # 预加载所有需要的文件类型替换内容
        self.file_replacements = {}
        for token_id, attrs in self.config.items():
            if 'replacementType' not in attrs or 'replacement' not in attrs:
                logging.error(f"配置项 token.{token_id} 缺少 'replacementType' 或 'replacement'")
                continue
            if attrs['replacementType'] == 'file':
                file_path = attrs['replacement']
                try:
                    self.file_replacements[token_id] = load_list_file(file_path)
                    logging.info(f"Loaded file replacements for token.{token_id} from {file_path}")
                except Exception as e:
                    logging.error(f"加载文件 {file_path} 失败: {e}")

        # 加载 rate_config
        self.rate_config = {}
        if self.rate_config_path and not self.stress_test:
            self._load_rate_config(self.rate_config_path)
        elif not self.stress_test:
            logging.warning("未提供 rate_config 文件，使用默认频率")
            # 设置默认频率
            self.rate_config = {
                'weekday_working': {'rate': '100', 'start_time': '09:00', 'end_time': '17:00'},
                'weekday_non_working': {'rate': '50'},
                'weekend_working': {'rate': '70', 'start_time': '10:00', 'end_time': '16:00'},
                'weekend_non_working': {'rate': '30'}
            }

        # 加载交易日列表（仅在 rate_config 中包含 trading_day 时使用）
        self.trading_days = set()
        self.use_trading_days = False
        if self.rate_config_path and self.trading_days_file and not self.stress_test:
            # 先加载 rate_config 来判断是否包含 trading_day
            if 'trading_day' in self.rate_config:
                self.use_trading_days = True
                try:
                    trading_days_list = load_list_file(self.trading_days_file)
                    # 确保日期格式为 YYYYMMDD
                    for day in trading_days_list:
                        if re.match(r'^\d{8}$', day):  # 简单的格式验证
                            self.trading_days.add(day)
                        else:
                            logging.warning(f"无效的交易日日期格式: {day}")
                    logging.debug(f"加载的交易日列表: {self.trading_days}")
                except Exception as e:
                    logging.error(f"加载交易日文件 {self.trading_days_file} 失败: {e}")
            else:
                logging.info("rate_config 中未包含 'trading_day' 配置，忽略交易日列表文件。")

    def _load_rate_config(self, rate_config_path):
        config = configparser.ConfigParser()
        config.read(rate_config_path)
        # Expected sections: trading_day, weekday_working, weekday_non_working, weekend_working, weekend_non_working
        expected_sections = ['trading_day', 'weekday_working', 'weekday_non_working', 'weekend_working', 'weekend_non_working']
        for section in expected_sections:
            if section in config:
                self.rate_config[section] = {}
                for key, value in config[section].items():
                    self.rate_config[section][key] = value
                logging.debug(f"加载频率配置: {section} = {self.rate_config[section]}")
            else:
                if section == 'trading_day':
                    # trading_day 是可选的，不存在时不报错
                    logging.info(f"配置文件中未包含可选的 section: {section}")
                else:
                    logging.warning(f"配置文件中缺少 section: {section}")

    def _load_template(self, template_path):
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"模板文件未找到: {template_path}")
        with open(template_path, 'r') as f:
            return f.read()

    def _replace_token(self, token, attrs):
        replacement_type = attrs['replacementType']
        replacement = attrs['replacement']
        
        if replacement_type == 'timestamp':
            formatted_time = get_current_time_format(replacement)
            return formatted_time
        
        elif replacement_type == 'file':
            replacement_list = self.file_replacements.get(token, [])
            if not replacement_list:
                logging.warning(f"文件替换列表为空: {replacement}")
                return replacement
            selected = random.choice(replacement_list)
            return selected
        
        elif replacement_type == 'random':
            # 格式: list["100","200","101","301","302","307","205"]
            list_values = re.findall(r'list\[(.*?)\]', replacement)
            if list_values:
                items = [item.strip().strip('"').strip("'") for item in list_values[0].split(',')]
                selected = random.choice(items)
                return selected
            else:
                logging.warning(f"随机替换格式错误: {replacement}")
                return replacement
        
        elif replacement_type == 'static':
            return replacement
        
        elif replacement_type == 'uuid':
            import uuid
            selected = str(uuid.uuid4())
            return selected
        
        elif replacement_type == 'number_range':
            # 格式: min-max，例如 1000-9999
            range_values = re.findall(r'(\d+)-(\d+)', replacement)
            if range_values:
                min_val, max_val = map(int, range_values[0])
                selected = str(random.randint(min_val, max_val))
                logging.info(f"替换 token {token} (number_range) 为 {selected}")
                return selected
            else:
                logging.warning(f"数字范围替换格式错误: {replacement}")
                return replacement
        
        else:
            logging.warning(f"未知的替换类型: {replacement_type}")
            return replacement

    def _generate_log(self):
        log = self.template
        tokens = re.findall(r'##(\w+)##', log)
        for token in tokens:
            # 找到对应的配置
            for token_id, attrs in self.config.items():
                if 'token' in attrs and attrs['token'] == f'##{token}##':
                    replacement = self._replace_token(token_id, attrs)
                    log = log.replace(f'##{token}##', replacement, 1)
                    break
            else:
                logging.warning(f"在配置中未找到对应的 token: ##{token}##")
        return log  # 返回完整的日志字符串

    def _get_current_rate(self):
        now = datetime.now()
        current_date_str = now.strftime('%Y%m%d')  # 修改为 YYYYMMDD 格式
        current_weekday = now.weekday()  # 0: Monday, 6: Sunday
        current_time_str = now.strftime('%H:%M')

        logging.info(f"当前日期: {current_date_str}, 星期: {current_weekday}, 时间: {current_time_str}")

        # 检查是否为交易日
        if current_date_str in self.trading_days:
            # 使用交易日频率
            trading_day_rate = self.rate_config.get('trading_day', {}).get('rate', '100')
            if '-' in trading_day_rate:
                min_rate, max_rate = map(int, trading_day_rate.split('-'))
                current_rate = random.randint(min_rate, max_rate)
            else:
                current_rate = int(trading_day_rate)
            interval = 60 / current_rate
            logging.info(f"当前为交易日，使用交易日频率: {current_rate} 条/分钟, 间隔: {interval:.2f} 秒")
            return current_rate, interval

        # 检查是否为工作日或周末
        if current_weekday < 5:
            # 工作日
            # 检查是否在工作时间
            start_time = self.rate_config.get('weekday_working', {}).get('start_time', '09:00')
            end_time = self.rate_config.get('weekday_working', {}).get('end_time', '17:00')
            if start_time <= current_time_str <= end_time:
                weekday_working_rate = self.rate_config.get('weekday_working', {}).get('rate', '100')
                if '-' in weekday_working_rate:
                    min_rate, max_rate = map(int, weekday_working_rate.split('-'))
                    current_rate = random.randint(min_rate, max_rate)
                else:
                    current_rate = int(weekday_working_rate)
                interval = 60 / current_rate
                logging.info(f"当前为工作日工作时间，使用工作日工作时间频率: {current_rate} 条/分钟, 间隔: {interval:.2f} 秒")
                return current_rate, interval
            else:
                weekday_non_working_rate = self.rate_config.get('weekday_non_working', {}).get('rate', '50')
                if '-' in weekday_non_working_rate:
                    min_rate, max_rate = map(int, weekday_non_working_rate.split('-'))
                    current_rate = random.randint(min_rate, max_rate)
                else:
                    current_rate = int(weekday_non_working_rate)
                interval = 60 / current_rate
                logging.info(f"当前为工作日非工作时间，使用工作日非工作时间频率: {current_rate} 条/分钟, 间隔: {interval:.2f} 秒")
                return current_rate, interval
        else:
            # 周末
            # 检查是否在工作时间
            start_time = self.rate_config.get('weekend_working', {}).get('start_time', '10:00')
            end_time = self.rate_config.get('weekend_working', {}).get('end_time', '16:00')
            if start_time <= current_time_str <= end_time:
                weekend_working_rate = self.rate_config.get('weekend_working', {}).get('rate', '70')
                if '-' in weekend_working_rate:
                    min_rate, max_rate = map(int, weekend_working_rate.split('-'))
                    current_rate = random.randint(min_rate, max_rate)
                else:
                    current_rate = int(weekend_working_rate)
                interval = 60 / current_rate
                logging.info(f"当前为周末工作时间，使用周末工作时间频率: {current_rate} 条/分钟, 间隔: {interval:.2f} 秒")
                return current_rate, interval
            else:
                weekend_non_working_rate = self.rate_config.get('weekend_non_working', {}).get('rate', '30')
                if '-' in weekend_non_working_rate:
                    min_rate, max_rate = map(int, weekend_non_working_rate.split('-'))
                    current_rate = random.randint(min_rate, max_rate)
                else:
                    current_rate = int(weekend_non_working_rate)
                interval = 60 / current_rate
                logging.info(f"当前为周末非工作时间，使用周末非工作时间频率: {current_rate} 条/分钟, 间隔: {interval:.2f} 秒")
                return current_rate, interval

    def start(self):
        logging.info("日志模拟器开始运行...")
        if self.stress_test:
            logging.info("压力测试模式已启用，尽可能快速地产生日志。")
            # 读取 stress_rate.ini 中的频率
            stress_config = configparser.ConfigParser()
            stress_config.read(self.stress_rate)
            stress_rate = stress_config.getint('stress_test', 'rate')  # 默认 100 条/分钟
            interval = 60 / stress_rate
            logging.info(f"压力测试模式，使用频率: {stress_rate} 条/分钟，间隔: {interval:.6f} 秒")
            try:
                while True:
                    log_event = self._generate_log()  # 生成单条日志事件
                    save_event_to_file(log_event, self.output_path)  # 直接写入单条日志
                    time.sleep(interval)  # 使用压测模式下的频率
            except KeyboardInterrupt:
                logging.info("压力测试模式已手动停止。")
        else:
            while True:
                rate, interval = self._get_current_rate()
                logging.info(f"当前生成频率: {rate} 条/分钟, 间隔: {interval:.2f} 秒")
                logging.info(f"已将日志写入文件: {self.output_path}")  # 可选，记录写入操作
                
                for _ in range(rate):
                    log_event = self._generate_log()  # 生成单条日志事件
                    save_event_to_file(log_event, self.output_path)  # 直接写入单条日志
                    time.sleep(interval)  # 按照设定间隔休眠
