"""
动作执行模块 - GUI 操作执行
"""

import enum
import time
import pyautogui
from typing import Optional, Tuple


class ActionType(enum.Enum):
    """操作类型"""

    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    DRAG = "drag"
    SCROLL = "scroll"
    WAIT = "wait"
    HOTKEY = "hotkey"
    DONE = "done"


class ActionExecutor:
    """GUI 动作执行器"""

    def __init__(self, move_duration: float = 0.3, default_delay: float = 0.5):
        """
        初始化执行器

        Args:
            move_duration: 鼠标移动时间
            default_delay: 默认操作延迟
        """
        self.move_duration = move_duration
        self.default_delay = default_delay
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        self._safe_mouse_position()

    def _safe_mouse_position(self):
        """将鼠标移到安全位置，避免触发 fail-safe"""
        current_x, current_y = pyautogui.position()
        screen_width, screen_height = pyautogui.size()

        if (
            current_x <= 10
            or current_x >= screen_width - 10
            or current_y <= 10
            or current_y >= screen_height - 10
        ):
            safe_x = screen_width // 2
            safe_y = screen_height // 2
            pyautogui.FAILSAFE = False
            pyautogui.moveTo(safe_x, safe_y, duration=0.1)
            pyautogui.FAILSAFE = True
            time.sleep(0.1)

    def click(
        self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left"
    ) -> None:
        """
        点击操作

        Args:
            x: X 坐标
            y: Y 坐标
            button: 鼠标按钮 (left, right, middle)
        """
        if x is not None and y is not None:
            pyautogui.moveTo(x, y, duration=self.move_duration)
        pyautogui.click(button=button)
        time.sleep(self.default_delay)

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """
        双击操作

        Args:
            x: X 坐标
            y: Y 坐标
        """
        if x is not None and y is not None:
            pyautogui.moveTo(x, y, duration=self.move_duration)
        pyautogui.doubleClick()
        time.sleep(self.default_delay)

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """
        右键点击

        Args:
            x: X 坐标
            y: Y 坐标
        """
        if x is not None and y is not None:
            pyautogui.moveTo(x, y, duration=self.move_duration)
        pyautogui.rightClick()
        time.sleep(self.default_delay)

    def type_text(self, text: str, interval: float = 0.05) -> None:
        """
        输入文本

        Args:
            text: 要输入的文本
            interval: 字符间隔
        """
        pyautogui.write(text, interval=interval)
        time.sleep(self.default_delay)

    def type_chinese(self, text: str) -> None:
        """
        输入中文文本 (使用剪贴板)

        Args:
            text: 要输入的中文文本
        """
        import pyperclip

        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(self.default_delay)

    def drag(
        self, start: Tuple[int, int], end: Tuple[int, int], duration: float = 0.5
    ) -> None:
        """
        拖拽操作

        Args:
            start: 起点坐标
            end: 终点坐标
            duration: 拖拽时间
        """
        pyautogui.moveTo(start[0], start[1], duration=self.move_duration)
        pyautogui.drag(
            end[0] - start[0], end[1] - start[1], duration=duration, button="left"
        )
        time.sleep(self.default_delay)

    def scroll(self, direction: str = "down", amount: int = 3) -> None:
        """
        滚动操作

        Args:
            direction: 滚动方向 (up, down, left, right)
            amount: 滚动量
        """
        if direction == "up":
            pyautogui.scroll(amount)
        elif direction == "down":
            pyautogui.scroll(-amount)
        elif direction == "left":
            pyautogui.hscroll(-amount)
        elif direction == "right":
            pyautogui.hscroll(amount)
        time.sleep(self.default_delay)

    def _normalize_key(self, key: str) -> str:
        """
        标准化键名，将常见别名转换为 pyautogui 识别的名称

        Args:
            key: 原始键名

        Returns:
            标准化后的键名
        """
        key_lower = key.lower().strip()

        # 键名映射表
        KEY_MAP = {
            "meta": "win",
            "super": "win",
            "cmd": "command",
            "command": "command",
            "opt": "option",
            "option": "option",
            "ctrl": "ctrl",
            "control": "ctrl",
            "alt": "alt",
            "shift": "shift",
            "enter": "enter",
            "return": "enter",
            "esc": "escape",
            "escape": "escape",
            "space": "space",
            "tab": "tab",
            "backspace": "backspace",
            "delete": "delete",
            "del": "delete",
            "insert": "insert",
            "home": "home",
            "end": "end",
            "pageup": "pageup",
            "pagedown": "pagedown",
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right",
            "f1": "f1",
            "f2": "f2",
            "f3": "f3",
            "f4": "f4",
            "f5": "f5",
            "f6": "f6",
            "f7": "f7",
            "f8": "f8",
            "f9": "f9",
            "f10": "f10",
            "f11": "f11",
            "f12": "f12",
        }

        return KEY_MAP.get(key_lower, key_lower)

    def hotkey(self, *keys: str) -> None:
        """
        组合键

        Args:
            keys: 按键序列
        """
        self._safe_mouse_position()
        normalized_keys = [self._normalize_key(k) for k in keys]
        pyautogui.hotkey(*normalized_keys)
        time.sleep(self.default_delay)

    def press(self, key: str) -> None:
        """
        按键

        Args:
            key: 按键名称
        """
        pyautogui.press(key)
        time.sleep(self.default_delay)

    def move_to(self, x: int, y: int) -> None:
        """
        移动鼠标

        Args:
            x: X 坐标
            y: Y 坐标
        """
        pyautogui.moveTo(x, y, duration=self.move_duration)

    def get_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置"""
        return pyautogui.position()

    def screenshot(self, region: Optional[Tuple[int, int, int, int]] = None):
        """
        截图

        Args:
            region: 截取区域

        Returns:
            PIL Image 对象
        """
        return pyautogui.screenshot(region=region)
