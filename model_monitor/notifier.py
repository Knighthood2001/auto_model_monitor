import yagmail
from datetime import datetime
import logging

class BaseNotifier:
    def send_notification(self, score: float, filename: str) -> bool:
        """发送通知，返回是否成功"""
        raise NotImplementedError

class EmailNotifier(BaseNotifier):
    def __init__(self, sender: str, receiver: str, auth_code: str, mode: str, threshold: float):
        self.sender = sender
        self.receiver = receiver
        self.auth_code = auth_code
        self.mode = mode
        self.threshold = threshold
        # 验证邮箱配置
        self._verify_email_config()

    def _verify_email_config(self):
        """验证邮箱配置有效性"""
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

    def send_notification(self, score: float, filename: str) -> bool:
        """发送邮件通知"""
        try:
            yag = yagmail.SMTP(
                user=self.sender,
                password=self.auth_code,
                host='smtp.qq.com'
            )
            
            # 根据模式调整邮件标题
            if self.mode == 'lower':
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
            logging.info(f"已发送通知：{filename}（分数：{score}）")
            return True
        except Exception as e:
            logging.error(f"邮件发送失败: {str(e)}")
            return False
