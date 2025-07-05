from auto_model_monitor import ModelMonitor, MonitorConfig, CustomParser
from datetime import datetime 
from typing import Tuple, List 

def custom_notification_generator(score: float, filename: str) -> Tuple[str, List[str]]:
    """根据分数和文件名生成自定义通知内容"""
    # 根据分数级别设置不同的优先级图标
    if score < 0.003:
        priority = "🔥🔥🔥 紧急"
        emoji = "🚀"
    elif score < 0.004:
        priority = "🚨 重要"
        emoji = "💡"
    else:
        priority = "ℹ️ 信息"
        emoji = "📌"
    
    # 主题
    subject = f"{priority}: {filename} 分数更新至 {score:.6f}"
    
    # 详细内容
    contents = [
        f"{emoji} 模型性能突破通知 {emoji}",
        "",
        f"文件名: {filename}",
        f"当前分数: {score:.6f}",
        f"阈值: 0.004",
        f"检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "📈 性能分析:",
        f"- 比阈值提升: {(0.004 - score) / 0.004 }",
        f"- 推荐操作: 考虑部署到测试环境",
        "",
        "此为自动通知，请勿回复。"
    ]
    
    return subject, contents
# 自定义解析器
parser = CustomParser(pattern=r'val_loss_([0-9.]+)_')

config = MonitorConfig(
    watch_dir='./quicktest/logs',                           # 监控的文件夹路径
    threshold=0.004,                                        # 阈值
    sender='2109695291@qq.com',                             # 发送邮箱
    receiver='2109695291@qq.com',                           # 接收邮箱
    auth_code='XXXX',                                       # 邮箱授权码
    check_interval=10,                                      # 检查间隔 (秒)
    log_dir='model_monitor_logs',                           # 日志文件夹路径
    comparison_mode='lower',                                # 比较模式
    parser=parser,                                          # 使用自定义解析器
    email_content_generator=custom_notification_generator   # 设置自定义通知生成器
)
monitor = ModelMonitor(config)
monitor.start_monitoring()
