import os
import time
import logging
from .parser import DefaultParser
from .notifier import EmailNotifier
from .config import MonitorConfig

class ModelMonitor:
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.parser = config.parser or DefaultParser()
        self.notifier = EmailNotifier(
            sender=config.sender,
            receiver=config.receiver,
            auth_code=config.auth_code,
            mode=config.comparison_mode,
            threshold=config.threshold  
        )
        
        # 初始化状态
        self.last_reported_score = float('inf') if config.comparison_mode == 'lower' else -float('inf')
        self.reported_files = set()
        
        # 初始化日志
        from .utils import setup_logger
        self.logger = setup_logger(config.log_dir)
        self.logger.info(f"模型监控器初始化完成")

    def _check_new_files(self):
        """检查文件夹中的新文件并判断是否需要通知"""
        current_best_score = float('inf') if self.config.comparison_mode == 'lower' else -float('inf')
        current_best_file = None
        
        for filename in os.listdir(self.config.watch_dir):
            file_path = os.path.join(self.config.watch_dir, filename)
            if not os.path.isfile(file_path):
                continue
                
            score, valid_filename = self.parser.parse(filename)
            if score is None:
                continue
                
            # 更新最佳分数
            if (self.config.comparison_mode == 'lower' and score < current_best_score) or \
               (self.config.comparison_mode == 'higher' and score > current_best_score):
                current_best_score = score
                current_best_file = valid_filename
        
        # 判断是否需要通知
        if (self.config.comparison_mode == 'lower' and current_best_score < self.config.threshold) or \
           (self.config.comparison_mode == 'higher' and current_best_score > self.config.threshold):
            
            if (self.config.comparison_mode == 'lower' and current_best_score < self.last_reported_score) or \
               (self.config.comparison_mode == 'higher' and current_best_score > self.last_reported_score):
                
                self.logger.info(f"发现更优分数: {current_best_score} (文件: {current_best_file})")
                if self.notifier.send_notification(current_best_score, current_best_file):
                    self.last_reported_score = current_best_score
                    self.reported_files.add(current_best_file)
            else:
                self.logger.info(f"已有更优分数, 无需通知: {current_best_score}")
        else:
            mode_desc = "低于" if self.config.comparison_mode == 'lower' else "高于"
            self.logger.info(f"未发现{mode_desc}阈值的分数 (当前最佳: {current_best_score}, 阈值: {self.config.threshold})")

    def start_monitoring(self):
        """启动监控循环"""
        self.logger.info(f"开始监控文件夹: {self.config.watch_dir} (阈值: {self.config.threshold})")
        try:
            while True:
                self._check_new_files()
                time.sleep(self.config.check_interval)
        except KeyboardInterrupt:
            self.logger.info("监控已手动停止")
        except Exception as e:
            self.logger.error(f"监控过程出错: {str(e)}", exc_info=True)
