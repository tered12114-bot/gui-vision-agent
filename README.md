# GUI Vision Agent

基于 qwen3.5-plus 视觉能力的 GUI 自动化 Agent，通过截图理解界面并执行点击、输入、拖拽等操作。

## 功能特性

- 🖼️ **视觉理解**: 截图分析界面，智能识别元素位置
- 🖱️ **自动化操作**: 点击、双击、输入、快捷键、拖拽、滚动
- 🇨🇳 **中文支持**: 自动检测中文并使用剪贴板输入
- ⚡ **快捷键映射**: 可配置系统快捷键（如 `win+d` 显示桌面）
- 🛡️ **安全机制**: 危险操作需要用户确认
- ⏱️ **时间统计**: 记录每个步骤的耗时

## 快速开始

### 安装依赖

```bash
pip install -r gui-vision/requirements.txt
```

Linux 需要安装剪贴板工具：

```bash
# X11
sudo apt-get install xclip

# Wayland
sudo apt-get install wl-clipboard
```

### 配置

复制配置模板：

```bash
cp gui-vision/config/config.yaml.example gui-vision/config/config.yaml
```

编辑配置文件，填入 API Key：

```yaml
api:
  api_key: "sk-sp-xxxxx"  # 阿里云百炼 Coding Plan API Key
  base_url: "https://coding.dashscope.aliyuncs.com/v1"
  model: "qwen3.5-plus"
```

### 使用

```python
from gui-vision.scripts.agent import VisionAgent

agent = VisionAgent(config_path="gui-vision/config/config.yaml")
result = agent.execute("打开Chrome浏览器并搜索Python教程")
```

## 配置说明

### API 配置

使用阿里云百炼 Coding Plan：
- API Key 格式: `sk-sp-xxxxx`
- Base URL: `https://coding.dashscope.aliyuncs.com/v1`

### 系统提示词配置

```yaml
system_prompt:
  enabled: true
  os: "Linux"           # Windows / macOS / Linux
  desktop: "KDE Plasma" # Windows 11 / GNOME / macOS Sonoma
  language: "zh_CN"
  
  custom_shortcuts:
    show_desktop: "win+d"
    open_terminal: "ctrl+alt+t"
    close_window: "alt+f4"
  
  custom_instructions: |
    - 任务栏在屏幕底部
    - QQ 最小化到系统托盘
```

## 支持的操作

| 操作 | 说明 |
|-----|------|
| `click` | 单击 |
| `double_click` | 双击 |
| `right_click` | 右键 |
| `type` | 输入文本（自动支持中文） |
| `hotkey` | 快捷键 |
| `scroll` | 滚动 |
| `drag` | 拖拽 |

## 文件结构

```
gui-vision/
├── SKILL.md              # OpenCode Skill 文档
├── scripts/
│   ├── agent.py          # Agent 主循环
│   ├── vision.py         # 截图处理
│   ├── action.py         # 操作执行
│   └── utils.py          # 工具函数
├── config/
│   └── config.yaml.example
└── requirements.txt
```

## 依赖

- openai >= 1.0.0
- mss >= 9.0.0
- pyautogui >= 0.9.54
- Pillow >= 10.0.0
- PyYAML >= 6.0
- pyperclip >= 1.8.0

## 注意事项

1. 需要屏幕截图和鼠标键盘控制权限
2. 屏幕分辨率自动检测
3. API 调用需要网络连接
4. Linux 需要安装 xclip 或 wl-clipboard

## License

MIT