import argparse
import os
import logging
from MSL.simulator import LogSimulator
from MSL.utils import setup_logging

__author__ = "Jelf"
__email__ = "heyjelf@gmail.com"
__date__ = "2024-10-09"

def parse_rate_config(rate_config_path):
    import configparser
    config = configparser.ConfigParser()
    config.read(rate_config_path)
    rate_periods = []
    for section in config.sections():
        period = {
            'start': config[section]['start'],
            'end': config[section]['end'],
            'rate': str(config[section]['rate'])
        }
        rate_periods.append(period)
    return rate_periods

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="日志模拟器")
    parser.add_argument('--template', type=str, required=True, help='日志模板文件路径')
    parser.add_argument('--config', type=str, required=True, help='配置文件路径')
    parser.add_argument('--output', type=str, required=True, help='输出日志文件路径')
    parser.add_argument('--rate_config', type=str, help='频率控制配置文件路径')
    parser.add_argument('--trading_days', type=str, help='交易日列表文件路径，可选')
    parser.add_argument('--stress_test', action='store_true', help='启用压力测试模式，尽可能快速地产生日志，可选')
    parser.add_argument('--stress_rate', type=str, help='配合stress_test使用，压测速率')
    
    args = parser.parse_args()
    
    rate_config = args.rate_config if args.rate_config else None
    
    trading_days_file = args.trading_days if args.trading_days else None

    stress_test = args.stress_test
    stress_rate = args.stress_rate
    
    simulator = LogSimulator(template_path=args.template, 
                             config_path=args.config, 
                             output_path=args.output, 
                             rate_config=rate_config,
                             trading_days_file=trading_days_file,
                             stress_test=stress_test,
                             stress_rate = stress_rate)
    simulator.start()

if __name__ == "__main__":
    main()
