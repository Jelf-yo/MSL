import configparser
import os
import logging

class Config:
    def __init__(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件未找到: {config_path}")
        
        # 禁用插值功能并保持键的大小写
        self.parser = configparser.ConfigParser(interpolation=None)
        self.parser.optionxform = str  # 保持键的大小写
        self.parser.read(config_path)
        self.tokens = self._parse_tokens()
        logging.debug(f"解析后的tokens: {self.tokens}")

    def _parse_tokens(self):
        tokens = {}
        for key in self.parser['default']:
            if key.startswith('token.'):
                parts = key.split('.')
                if len(parts) < 3:
                    logging.warning(f"配置项格式不正确: {key}")
                    continue
                token_num = parts[1]
                attribute = parts[2]
                if token_num not in tokens:
                    tokens[token_num] = {}
                tokens[token_num][attribute] = self.parser['default'][key]
                logging.debug(f"Parsed token.{token_num}.{attribute} = {self.parser['default'][key]}")
        return tokens

    def get_tokens(self):
        return self.tokens
