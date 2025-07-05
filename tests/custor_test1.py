from auto_model_monitor import ModelMonitor, MonitorConfig, CustomParser
# 自定义解析器
parser = CustomParser(pattern=r'val_loss_([0-9.]+)_')
# 自定义主题和内容模板
subject_template = "🔥 重要通知：{filename} 分数{condition}阈值！"

content_template = """
📊 模型更新详情 📊

- 文件名：{filename}
- 当前分数：{score:.6f}
- 阈值：{threshold:.6f}
- 状态：分数{condition}阈值，建议查看！

⏰ 检测时间：{timestamp}
"""

config = MonitorConfig(
    watch_dir='./quicktest/logs',             # 监控的文件夹路径
    threshold=0.004,                          # 阈值
    sender='2109695291@qq.com',               # 发送邮箱
    receiver='2109695291@qq.com',             # 接收邮箱
    auth_code='XXXX',                         # 邮箱授权码
    check_interval=10,                        # 检查间隔 (秒)
    log_dir='model_monitor_logs',             # 日志文件夹路径
    comparison_mode='lower',                  # 比较模式
    parser=parser,                            # 使用自定义解析器
    email_subject_template=subject_template,  # 设置主题模板
    email_content_template=content_template   # 设置内容模板
)
monitor = ModelMonitor(config)
monitor.start_monitoring()
