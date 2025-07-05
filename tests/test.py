from model_monitor import ModelMonitor, MonitorConfig, CustomParser

# 自定义解析器
parser = CustomParser(pattern=r'val_loss_([0-9.]+)_')

# 配置参数
config = MonitorConfig(
    watch_dir='./quicktest/logs',
    threshold=0.004,
    sender='2109695291@qq.com',
    receiver='2109695291@qq.com',
    auth_code='xxxx',
    check_interval=5,
    log_dir='model_monitor_logs',
    comparison_mode='lower',
    parser=parser  # 使用自定义解析器
)

# 初始化并启动监控器
monitor = ModelMonitor(config)
monitor.start_monitoring()
