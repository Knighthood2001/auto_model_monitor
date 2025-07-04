import os
import re
import time
import logging
from datetime import datetime
import yagmail

class ModelMonitor:
    def __init__(self, watch_dir, threshold, sender, receiver, auth_code, 
                 check_interval=60, log_dir='monitor_logs', comparison_mode='lower',re_parser=None):
        """
        模型权重监控器初始化
        :param watch_dir: 监控的文件夹路径
        :param threshold: 分数阈值
        :param sender: 发送邮箱
        :param receiver: 接收邮箱
        :param auth_code: 邮箱授权码
        :param check_interval: 检查间隔 (秒) , 默认60秒
        :param log_dir: 日志文件夹路径
        :param comparison_mode: 比较模式, 可选 'lower' (低于阈值) 或 'higher' (高于阈值), 默认为 'lower'
        :param re_parser: 正则表达式解析器, 用于从文件名中提取指定内容, 默认为 None (不使用正则表达式)
        """
        self.watch_dir = watch_dir
        self.threshold = threshold
        self.sender = sender
        self.receiver = receiver
        self.auth_code = auth_code
        self.check_interval = check_interval
        self.log_dir = log_dir
        # 验证比较模式合法性
        if comparison_mode not in ['lower', 'higher']:
            raise ValueError("comparison_mode 必须是 'lower' 或 'higher'")
        self.comparison_mode = comparison_mode

        # 初始化状态变量
        if self.comparison_mode == 'lower':
            self.last_reported_score = float('inf')  # 低于模式：初始为无穷大（越小越好）
        else:
            self.last_reported_score = -float('inf')  # 高于模式：初始为负无穷大（越大越好）

        self.reported_files = set()  # 记录已播报过的文件
        
        # 初始化日志系统
        self._init_logger()
        
        # 验证邮箱配置
        self._verify_email_config()
        self.re_parser = re_parser or self._default_re_parser


    def _init_logger(self):
        """初始化日志系统, 日志文件名精确到时分秒, 支持按日期分类文件夹"""
        # 1. 创建日志根目录 (如不存在) 
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # 2. 按日期创建子文件夹 (可选, 方便按日期归档) 
        date_str = datetime.now().strftime('%Y%m%d')
        daily_log_dir = os.path.join(self.log_dir, date_str)
        if not os.path.exists(daily_log_dir):
            os.makedirs(daily_log_dir)
        
        # 3. 日志文件名精确到“年月日时分秒”, 确保每次运行生成唯一文件
        # 格式示例: monitor_20250704153022.log (2025年7月4日15点30分22秒) 
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        log_filename = f"monitor_{timestamp}.log"
        log_path = os.path.join(daily_log_dir, log_filename)  # 日志文件路径
        
        # 4. 配置日志格式 (避免重复添加Handler) 
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # 设置全局日志级别
        
        # 清除已有Handler (防止重复输出) 
        if logger.hasHandlers():
            logger.handlers.clear()
        
        # 5. 添加文件Handler (写入日志文件) 
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # 6. 添加控制台Handler (同时输出到控制台) 
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        logging.info(f"模型监控器初始化完成, 日志文件路径: {log_path}")

    def _verify_email_config(self):
        """验证邮箱配置是否有效"""
        try:
            yag = yagmail.SMTP(
                user=self.sender,
                password=self.auth_code,
                host='smtp.qq.com'
            )
            yag.close()
            logging.info("邮箱配置验证成功")
        except Exception as e:
            logging.error(f"邮箱配置验证失败: {str(e)}")
            raise ValueError("请检查邮箱授权码或SMTP配置")

    def _default_re_parser(self, filename):
        """从文件名中解析分数"""
        match = re.match(r'ckpt_([0-9.]+)_\d+\.pt', filename)
        if match:
            try:
                return float(match.group(1)), filename
            except ValueError:
                logging.warning(f"文件名 {filename} 格式无法解析")
        return None, None

    def _send_notification(self, score, filename):
        """发送邮件通知（根据模式调整标题和内容）"""
        try:
            yag = yagmail.SMTP(
                user=self.sender,
                password=self.auth_code,
                host='smtp.qq.com'
            )
            # 根据模式调整邮件标题
            if self.comparison_mode == 'lower':
                subject = f'模型分数低于阈值警告 ({score})'
                condition = '低于阈值'
            else:
                subject = f'模型分数高于阈值通知 ({score})'
                condition = '高于阈值'
            
            contents = [
                f'检测到新的模型文件分数{condition}：',
                f'文件名：{filename}',
                f'当前分数：{score}',
                f'阈值：{self.threshold}',
                f'检测时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            ]
            yag.send(to=self.receiver, subject=subject, contents=contents)
            yag.close()
            logging.info(f"已发送通知：{filename}（分数：{score}，模式：{self.comparison_mode}）")
            return True
        except Exception as e:
            logging.error(f"邮件发送失败：{str(e)}")
            return False
    def _check_new_files(self):
        """检查文件夹中的新文件并判断是否需要通知（根据模式动态调整逻辑）"""
        # 根据模式定义“当前最佳分数”的初始值
        if self.comparison_mode == 'lower':
            current_best_score = float('inf')  # 寻找更小的分数
        else:
            current_best_score = -float('inf')  # 寻找更大的分数
        current_best_file = None
        
        # 遍历文件夹中的文件
        for filename in os.listdir(self.watch_dir):
            file_path = os.path.join(self.watch_dir, filename)
            if not os.path.isfile(file_path):
                continue
            
            score, valid_filename = self.re_parser(filename)
            if score is None:
                continue
            
            # 根据模式更新“当前最佳分数”
            if self.comparison_mode == 'lower':
                # 低于模式：分数越小越优
                if score < current_best_score:
                    current_best_score = score
                    current_best_file = valid_filename
            else:
                # 高于模式：分数越大越优
                if score > current_best_score:
                    current_best_score = score
                    current_best_file = valid_filename
        
        # 根据模式判断是否需要通知
        need_notify = False
        if self.comparison_mode == 'lower':
            # 低于模式：当前最佳分数 < 阈值 时需要判断
            need_notify = current_best_score < self.threshold
        else:
            # 高于模式：当前最佳分数 > 阈值 时需要判断
            need_notify = current_best_score > self.threshold
        
        if need_notify:
            # 根据模式判断是否“优于上次播报”
            is_better = False
            if self.comparison_mode == 'lower':
                # 低于模式：当前分数 < 上次分数 → 更优
                is_better = current_best_score < self.last_reported_score
            else:
                # 高于模式：当前分数 > 上次分数 → 更优
                is_better = current_best_score > self.last_reported_score
            
            if is_better:
                logging.info(f"发现更优分数: {current_best_score} (文件: {current_best_file})")
                if self._send_notification(current_best_score, current_best_file):
                    self.last_reported_score = current_best_score
                    self.reported_files.add(current_best_file)
            else:
                logging.info(f"已存在相同或更优分数, 无需重复通知 (当前最佳: {current_best_score})")
        else:
            # 未达到阈值时的日志（根据模式调整描述）
            if self.comparison_mode == 'lower':
                msg = f"未发现低于阈值的分数 (当前最佳: {current_best_score}, 阈值: {self.threshold})"
            else:
                msg = f"未发现高于阈值的分数 (当前最佳: {current_best_score}, 阈值: {self.threshold})"
            logging.info(msg)

    def start_monitoring(self):
        """启动监控循环"""
        logging.info(f"开始监控文件夹: {self.watch_dir} (阈值: {self.threshold}, 检查间隔: {self.check_interval}秒) ")
        try:
            while True:
                self._check_new_files()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logging.info("监控已手动停止")
        except Exception as e:
            logging.error(f"监控过程出错: {str(e)}", exc_info=True)


if __name__ == '__main__':
    # 如果需要自定义配置，请在这里修改
    def re_parser(filename):
        # 例如文件名格式：epoch_10_val_loss_0.003_acc_0.95.pt
        match = re.search(r'val_loss_([0-9.]+)_', filename)
        if match:
            return float(match.group(1)), filename
        return None, None
    # 配置参数
    CONFIG = {
        'watch_dir': './DPUNet_2025_07_04__15_51_01',  # 监控的文件夹
        'threshold': 0.004,  # 分数阈值
        'sender': '2109695291@qq.com',  # 发送邮箱
        'receiver': '2109695291@qq.com',  # 接收邮箱
        'auth_code': 'xxxx',  # 请填写QQ邮箱授权码
        'check_interval': 5,  # 检查间隔 (秒) 
        'log_dir': 'model_monitor_logs',  # 日志文件夹
        'comparison_mode': 'lower',
        # 're_parser': re_parser
    }

    # 初始化并启动监控器
    monitor = ModelMonitor(**CONFIG)
    monitor.start_monitoring()
