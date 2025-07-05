# auto_model_monitor

监视模型训练时生成的权重文件，符合条件时发送QQ邮件通知。

# 使用场景

**当你希望在模型训练过程中，当某个指标（例如验证集上的损失或准确率）低于/高于预设阈值时收到邮件通知。这有助于你及时了解模型的性能表现，以便进行必要的调整。**

# 如何使用
## 安装依赖
```bash
pip install auto_model_monitor
```

## 获取QQ授权码
为了给QQ邮箱发送邮件，你需要使用授权码而不是密码。你可以在QQ邮箱的设置中找到它。

**[https://service.mail.qq.com/detail/0/75](https://service.mail.qq.com/detail/0/75)**

<!-- ![Alt text](img/1.jpg) -->

<img src="https://github.com/Knighthood2001/auto_model_monitor/blob/main/img/1.jpg" alt="QQ授权码" width="50%">



## 示例代码
上述配置后，你就可以使用代码了。

### 基础使用
测试代码在[tests/basic_test.py](tests/basic_test.py)

```python
from auto_model_monitor import ModelMonitor, MonitorConfig, CustomParser

# 自定义解析器(TODO: 替换为你的自定义解析器')
parser = CustomParser(pattern=r'val_loss_([0-9.]+)_')

# 配置参数
config = MonitorConfig(
    watch_dir='./quicktest/logs',     # 监控的文件夹路径
    threshold=0.004,                  # 阈值
    sender='aaaa@qq.com',       # 发送邮箱
    receiver='aaaa@qq.com',     # 接收邮箱
    auth_code='xxxx',                 # 邮箱授权码(TODO: 替换为你的授权码')
    check_interval=5,                 # 检查间隔 (秒)
    log_dir='model_monitor_logs',     # 日志文件夹路径
    comparison_mode='lower',          # 比较模式
    parser=parser                     # 使用自定义解析器
)

# 初始化并启动监控器
monitor = ModelMonitor(config)
monitor.start_monitoring()
```
**注意：** 你需要修改解析器，以及你自己的邮箱授权码。

当你的模型权重文件中的分数低于或高于阈值时，你将收到邮件通知。例如：

<!-- ![Alt text](img/2.jpg) -->

<img src="https://github.com/Knighthood2001/auto_model_monitor/blob/main/img/2.jpg" alt="图2" width="50%">


### 自定义使用1
测试代码在[tests/custom_test1.py](tests/custom_test1.py)

你可以自定义邮件的主题和内容模板。例如：
```python
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
```

收到的邮件内容如下所示：

<!-- ![Alt text](img/111.jpg) -->

<img src="https://github.com/Knighthood2001/auto_model_monitor/blob/main/img/111.jpg" alt="自定义使用图1" width="50%">


### 自定义使用2

测试代码在[tests/custom_test2.py](tests/custom_test2.py)

你可以自定义邮件的内容生成器。例如：
```python
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
```

收到的邮件内容如下所示：

<!-- ![Alt text](img/222.jpg) -->

<img src="https://github.com/Knighthood2001/auto_model_monitor/blob/main/img/222.jpg" alt="自定义使用图2" width="50%">

# 开发日志

2025-07-04 更新：
- 最初版本发布。

2025-07-05 更新：
- 代码重构。如果你需要重构前的代码，在[tests/quicktest](tests/quicktest/demo.py)中查看。
- 代码打包，上传PyPI。
- 由于`model_monitor`这个名字已经被占用，改为`auto_model_monitor`。
- 发布v0.2.0版本。

# PyPI库版本
v0.1.0
- 基础版本

v0.1.1
- 代码重构

v0.1.2
- 完善README.md

v0.2.0
- 添加自定义主题和内容，方便用户自定义邮件内容

v0.2.1
- 修复PyPI图片无法显示问题
