"""
视觉模块 - 截图和图像处理
"""

import mss
import base64
from io import BytesIO
from PIL import Image
from typing import Optional, Tuple


def capture_screen(
    monitor: int = 1, region: Optional[Tuple[int, int, int, int]] = None
) -> Image.Image:
    """
    截取屏幕

    Args:
        monitor: 显示器编号 (1 = 主显示器)
        region: 截取区域 (left, top, width, height)

    Returns:
        PIL Image 对象
    """
    with mss.mss() as sct:
        if region:
            screenshot = sct.grab(
                {
                    "left": region[0],
                    "top": region[1],
                    "width": region[2],
                    "height": region[3],
                }
            )
        else:
            screenshot = sct.grab(sct.monitors[monitor])

        return Image.frombytes("RGB", screenshot.size, screenshot.rgb)


def capture_all_monitors() -> Image.Image:
    """截取所有显示器"""
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[0])
        return Image.frombytes("RGB", screenshot.size, screenshot.rgb)


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """
    将图像转换为 base64 字符串

    Args:
        image: PIL Image 对象
        format: 图像格式

    Returns:
        base64 编码字符串
    """
    buffer = BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def base64_to_image(b64_string: str) -> Image.Image:
    """
    将 base64 字符串转换为图像

    Args:
        b64_string: base64 编码字符串

    Returns:
        PIL Image 对象
    """
    image_data = base64.b64decode(b64_string)
    return Image.open(BytesIO(image_data))


def resize_for_model(
    image: Image.Image, max_size: Tuple[int, int] = (1920, 1080)
) -> Image.Image:
    """
    调整图像大小以适应模型输入限制

    Args:
        image: 原始图像
        max_size: 最大尺寸

    Returns:
        调整后的图像
    """
    if image.size[0] <= max_size[0] and image.size[1] <= max_size[1]:
        return image

    ratio = min(max_size[0] / image.size[0], max_size[1] / image.size[1])
    new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
    return image.resize(new_size, Image.Resampling.LANCZOS)
