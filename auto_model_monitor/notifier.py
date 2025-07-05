import yagmail
from datetime import datetime
import logging
from typing import List, Tuple

class BaseNotifier:
    def send_notification(self, score: float, filename: str) -> bool:
        """发送通知，返回是否成功"""
        raise NotImplementedError

class EmailNotifier(BaseNotifier):
    def __init__(self, sender: str, receiver: str, auth_code: str, mode: str, threshold: float, 
        subject_template: str = None, content_template: str = None, content_generator: callable = None,
        logger=None
    ):
        self.sender = sender
        self.receiver = receiver
        self.auth_code = auth_code
        self.mode = mode
        self.threshold = threshold
        self.subject_template = subject_template    # 邮件标题模板
        self.content_template = content_template    # 邮件内容模板
        self.content_generator = content_generator  # 邮件内容生成器
        self.logger = logger or logging.getLogger(__name__)
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

    def _get_default_subject(self, score: float, filename: str) -> str:
        """生成默认邮件主题"""
        condition = "低于" if self.mode == 'lower' else "高于"
        return f'模型监控通知：{condition}阈值'

    def _get_default_contents(self, score: float, filename: str) -> List[str]:
        """生成默认邮件内容"""
        condition = "低于" if self.mode == 'lower' else "高于"
        return [
            f'检测到新的模型文件分数{condition}阈值：',
            f'文件名：{filename}',
            f'当前分数：{score}',
            f'阈值：{self.threshold}',
            f'检测时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        ]

    def send_notification(self, score: float, filename: str) -> bool:
        """发送通知邮件"""
        try:
            # 检查是否使用自定义生成器同时生成主题和内容
            if self.content_generator:
                result = self.content_generator(score, filename)
                
                # 处理返回类型
                if isinstance(result, tuple) and len(result) == 2:
                    subject, contents = result  # 解包元组
                else:
                    # 兼容只返回内容的旧函数
                    subject = self._get_default_subject(score, filename)
                    contents = result
            else:
                # 使用模板或默认方式生成主题和内容
                if self.subject_template:
                    subject = self.subject_template.format(
                        score=score, 
                        filename=filename, 
                        threshold=self.threshold,
                        condition="低于" if self.mode == 'lower' else "高于"
                    )
                else:
                    subject = self._get_default_subject(score, filename)

                if self.content_template:
                    contents = self.content_template.format(
                        score=score, 
                        filename=filename, 
                        threshold=self.threshold,
                        condition="低于" if self.mode == 'lower' else "高于",
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    if isinstance(contents, str):
                        contents = contents.split('\n')
                else:
                    contents = self._get_default_contents(score, filename)

            # 发送邮件
            yag = yagmail.SMTP(
                user=self.sender,
                password=self.auth_code,
                host='smtp.qq.com',
                port=465,
                smtp_ssl=True
            )
            yag.send(
                to=self.receiver,
                subject=subject,
                contents=contents
            )
            yag.close()
            self.logger.info(f"已发送通知: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"邮件发送失败: {str(e)}")
            return False