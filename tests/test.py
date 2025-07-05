from auto_model_monitor import ModelMonitor, MonitorConfig, CustomParser

# 自定义解析器
parser = CustomParser(pattern=r'val_loss_([0-9.]+)_')

# 配置参数
config = MonitorConfig(
    watch_dir='./quicktest/logs',     # 监控的文件夹路径
    threshold=0.004,                  # 阈值
    sender='2109695291@qq.com',       # 发送邮箱
    receiver='2109695291@qq.com',     # 接收邮箱
    auth_code='xxxx',                 # 邮箱授权码
    check_interval=5,                 # 检查间隔 (秒)
    log_dir='model_monitor_logs',     # 日志文件夹路径
    comparison_mode='lower',          # 比较模式
    parser=parser                     # 使用自定义解析器
)

# 初始化并启动监控器
monitor = ModelMonitor(config)
monitor.start_monitoring()
