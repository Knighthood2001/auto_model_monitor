import re
import logging

class BaseParser:
    def parse(self, filename: str):
        """从文件名中解析分数，返回 (score, filename) 或 (None, None)"""
        raise NotImplementedError

class DefaultParser(BaseParser):
    """默认解析器，匹配 ckpt_<score>_<epoch>.pt 格式"""
    def parse(self, filename: str):
        match = re.match(r'ckpt_([0-9.]+)_\d+\.pt', filename)
        if match:
            try:
                return float(match.group(1)), filename
            except ValueError:
                logging.warning(f"文件名格式无法解析: {filename}")
        return None, None

class CustomParser(BaseParser):
    """自定义解析器，匹配 val_loss_<score>_acc_<acc>.pt 格式"""
    def __init__(self, pattern=r'val_loss_([0-9.]+)_'):
        self.pattern = pattern
    
    def parse(self, filename: str):
        match = re.search(self.pattern, filename)
        if match:
            return float(match.group(1)), filename
        return None, None
