from dataclasses import dataclass
from typing import Callable, Optional
from .parser import BaseParser, DefaultParser

@dataclass
class MonitorConfig:
    """模型监控器配置类"""
    watch_dir: str
    threshold: float
    sender: str
    receiver: str
    auth_code: str
    check_interval: int = 60
    log_dir: str = 'monitor_logs'
    comparison_mode: str = 'lower'
    parser: Optional[BaseParser] = None
    
    def __post_init__(self):
        # 验证比较模式
        if self.comparison_mode not in ['lower', 'higher']:
            raise ValueError("comparison_mode 必须是 'lower' 或 'higher'")
            
        # 设置默认解析器
        if self.parser is None:
            self.parser = DefaultParser()
