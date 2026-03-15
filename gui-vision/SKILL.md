---
name: gui-vision
description: |
  视觉 GUI 操作技能 - 通过 AI 视觉能力自动化操作桌面界面。
  
  **重要：当用户提到以下任何内容时，必须使用此技能：**
  
  - 点击、双击、右键点击屏幕上的元素
  - 打开应用、切换窗口、关闭窗口
  - 在输入框中输入文本（包括中文）
  - 填写表单、搜索框输入
  - 拖拽文件、滚动页面
  - 截图分析界面、描述屏幕内容
  - 自动化桌面操作任务
  - GUI 测试、界面操作演示
  
  即使没有明确提到"视觉"、"GUI"、"桌面"等词，只要涉及屏幕操作、界面交互、应用控制等任务，也应该使用此技能。不要假设用户可以手动完成这些操作——主动提供自动化帮助。
---

# GUI 视觉操作技能

基于 qwen3.5-plus 视觉能力的 GUI 自动化 Agent，通过截图理解界面并执行操作。

## 快速开始

```python
from scripts.agent import VisionAgent

agent = VisionAgent(config_path="config/config.yaml")
result = agent.execute("打开Chrome浏览器并搜索Python教程")
```

## 工作流程

```
Observe → Think → Act → Verify → (循环直到完成)
  ↓         ↓        ↓        ↓
截图     模型决策   执行操作   验证结果
```

### 执行步骤

1. **Observe**: 截取当前屏幕
2. **Think**: 发送截图给视觉模型分析，决定下一步操作
3. **Act**: 执行点击、输入、快捷键等操作
4. **Verify**: 检查操作结果，决定是否继续

## 支持的操作

| 操作类型 | 说明 | 示例 |
|---------|------|------|
| `click` | 单击 | 点击按钮、图标 |
| `double_click` | 双击 | 打开文件 |
| `right_click` | 右键 | 显示菜单 |
| `type` | 输入文本 | 填写表单（自动支持中文） |
| `hotkey` | 快捷键 | Ctrl+C、Win+D |
| `scroll` | 滚动 | 上下左右滚动 |
| `drag` | 拖拽 | 移动文件 |
| `wait` | 等待 | 等待界面加载 |

## 配置

### 配置文件 (config/config.yaml)

```yaml
api:
  api_key: "your-api-key"
  base_url: "https://coding.dashscope.aliyuncs.com/v1"
  model: "qwen3.5-plus"

screen:
  width: 1920
  height: 1080

safety:
  auto_confirm_low_risk: true
  require_confirmation: ["delete", "close", "shutdown", "format"]

timing:
  action_delay: 0.5
  screenshot_delay: 1.0
  max_wait_time: 10.0

agent:
  max_steps: 50
  max_retries: 3

system_prompt:
  enabled: true
  os: "Linux"
  desktop: "KDE Plasma"
  language: "zh_CN"
  custom_shortcuts:
    show_desktop: "win+d"
    open_terminal: "ctrl+alt+t"
    switch_window: "alt+tab"
    close_window: "alt+f4"
    open_file_manager: "win+e"
  custom_instructions: |
    - 任务栏在屏幕底部
    - 常用应用：Dolphin(文件管理器)、Chrome(浏览器)
```

### 环境变量

```bash
export QWEN_API_KEY="sk-sp-xxxxx"
```

### 阿里云百炼 Coding Plan

此技能使用阿里云百炼 Coding Plan 的 API：
- Base URL: `https://coding.dashscope.aliyuncs.com/v1`
- API Key 格式: `sk-sp-xxxxx`
- 支持模型: qwen3.5-plus

## 系统提示词配置

通过 `system_prompt` 配置告诉视觉模型你的系统环境：

```yaml
system_prompt:
  enabled: true
  os: "Windows"  # 或 "Linux", "macOS"
  desktop: "Windows 11"  # 或 "KDE Plasma", "GNOME", "macOS Sonoma"
  language: "zh_CN"
  
  custom_shortcuts:
    show_desktop: "win+d"      # Windows/Linux
    # show_desktop: "f11"      # macOS
    open_terminal: "ctrl+alt+t"
    close_window: "alt+f4"
  
  custom_instructions: |
    - 任务栏位置、常用应用名称
    - 特殊操作方式
    - 应用最小化位置（如系统托盘）
```

## 坐标系统

模型返回 **1000×1000 归一化坐标** `[y, x]`：

```python
# 自动转换
pixel_x = norm_x * screen_width / 1000
pixel_y = norm_y * screen_height / 1000
```

## 安全机制

| 操作 | 风险级别 | 确认策略 |
|-----|---------|---------|
| click, type, scroll, hotkey | 低 | 自动执行 |
| double_click, drag | 中 | 可配置 |
| delete, close, shutdown, format | 高 | 必须确认 |

## 使用示例

```python
# 简单操作
agent.execute("点击保存按钮")

# 中文输入（自动处理）
agent.execute("在搜索框输入'你好世界'")

# 多步骤任务
agent.execute("打开文件管理器，进入Documents文件夹，找到report.docx并双击打开")

# 使用快捷键
agent.execute("使用Win+D显示桌面，然后描述壁纸")
```

## 错误处理

- 达到 `max_steps` 限制时自动停止
- 操作失败可重试（`max_retries`）
- 支持 Ctrl+C 中断

## 依赖

```
openai>=1.0.0
mss>=9.0.0
pyautogui>=0.9.54
Pillow>=10.0.0
PyYAML>=6.0
pyperclip>=1.8.0
```

## 文件结构

```
gui-vision/
├── SKILL.md
├── scripts/
│   ├── agent.py      # 主循环
│   ├── vision.py     # 截图处理
│   ├── action.py     # 操作执行
│   └── utils.py      # 工具函数
├── config/
│   └── config.yaml.example
└── requirements.txt
```

## 注意事项

1. **权限**: 需要屏幕截图和鼠标键盘控制权限
2. **分辨率**: 自动检测，无需手动配置
3. **网络**: API 调用需要网络连接
4. **Linux 剪贴板**: 需安装 `xclip` 或 `wl-clipboard`
5. **安全机制**: 危险操作会请求确认