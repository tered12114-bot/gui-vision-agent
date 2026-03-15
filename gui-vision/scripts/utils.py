"""
工具函数模块
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


def normalize_to_pixel(
    norm_y: int, norm_x: int, screen_width: int, screen_height: int
) -> Tuple[int, int]:
    """
    将归一化坐标转换为像素坐标

    模型返回的是 1000x1000 的归一化坐标 [y, x]

    Args:
        norm_y: 归一化 Y 坐标 (0-1000)
        norm_x: 归一化 X 坐标 (0-1000)
        screen_width: 屏幕宽度 (像素)
        screen_height: 屏幕高度 (像素)

    Returns:
        (pixel_x, pixel_y) 像素坐标
    """
    pixel_x = int(norm_x * screen_width / 1000)
    pixel_y = int(norm_y * screen_height / 1000)

    pixel_x = max(0, min(pixel_x, screen_width - 1))
    pixel_y = max(0, min(pixel_y, screen_height - 1))

    return pixel_x, pixel_y


def pixel_to_normalize(
    pixel_x: int, pixel_y: int, screen_width: int, screen_height: int
) -> Tuple[int, int]:
    """
    将像素坐标转换为归一化坐标

    Args:
        pixel_x: 像素 X 坐标
        pixel_y: 像素 Y 坐标
        screen_width: 屏幕宽度
        screen_height: 屏幕高度

    Returns:
        (norm_y, norm_x) 归一化坐标 (0-1000)
    """
    norm_x = int(pixel_x * 1000 / screen_width)
    norm_y = int(pixel_y * 1000 / screen_height)
    return norm_y, norm_x


def get_screen_size() -> Tuple[int, int]:
    """获取主显示器屏幕尺寸"""
    try:
        import pyautogui

        return pyautogui.size()
    except Exception:
        return 1920, 1080


DEFAULT_CONFIG = {
    "api": {
        "api_key": "",
        "base_url": "https://coding.dashscope.aliyuncs.com/v1",
        "model": "qwen3.5-plus",
    },
    "screen": {"width": 1920, "height": 1080},
    "safety": {
        "auto_confirm_low_risk": True,
        "require_confirmation": ["delete", "close", "shutdown", "format"],
    },
    "timing": {
        "action_delay": 0.5,
        "screenshot_delay": 1.0,
        "max_wait_time": 10.0,
    },
    "agent": {
        "max_steps": 50,
        "max_retries": 3,
    },
    "system_prompt": {
        "enabled": True,
        "os": "Linux",
        "desktop": "KDE Plasma",
        "language": "zh_CN",
        "custom_shortcuts": {
            "show_desktop": "meta+d",
            "open_terminal": "ctrl+alt+t",
            "switch_window": "alt+tab",
            "close_window": "alt+f4",
            "open_file_manager": "meta+e",
        },
        "custom_instructions": "",
    },
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载配置

    优先级:
    1. 指定的配置文件
    2. 环境变量
    3. 默认配置

    Args:
        config_path: 配置文件路径

    Returns:
        配置字典
    """
    config = DEFAULT_CONFIG.copy()

    if config_path and Path(config_path).exists():
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f)
            config = deep_merge(config, user_config)

    if os.environ.get("QWEN_API_KEY"):
        config["api"]["api_key"] = os.environ["QWEN_API_KEY"]
    if os.environ.get("QWEN_BASE_URL"):
        config["api"]["base_url"] = os.environ["QWEN_BASE_URL"]

    screen_width, screen_height = get_screen_size()
    config["screen"]["width"] = screen_width
    config["screen"]["height"] = screen_height

    return config


def deep_merge(base: Dict, override: Dict) -> Dict:
    """
    深度合并字典

    Args:
        base: 基础字典
        override: 覆盖字典

    Returns:
        合并后的字典
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def validate_coordinates(x: int, y: int, screen_width: int, screen_height: int) -> bool:
    """
    验证坐标是否在屏幕范围内

    Args:
        x: X 坐标
        y: Y 坐标
        screen_width: 屏幕宽度
        screen_height: 屏幕高度

    Returns:
        是否有效
    """
    return 0 <= x < screen_width and 0 <= y < screen_height
