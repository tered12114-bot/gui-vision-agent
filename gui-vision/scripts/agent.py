"""
视觉 GUI 操作 Agent

基于 qwen-3.5-plus 视觉能力的通用 GUI 操作 Agent
"""

import time
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

from openai import OpenAI

from .vision import capture_screen, image_to_base64
from .action import ActionExecutor, ActionType
from .utils import normalize_to_pixel, load_config


@dataclass
class Action:
    """操作记录"""

    type: ActionType
    x: Optional[int] = None
    y: Optional[int] = None
    text: Optional[str] = None
    reasoning: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class AgentState:
    """Agent 状态"""

    history: List[Action] = field(default_factory=list)
    current_step: int = 0
    max_steps: int = 50
    context: Dict[str, Any] = field(default_factory=dict)
    last_screenshot: Optional[str] = None


@dataclass
class StepTiming:
    """步骤时间记录"""

    observe_time: float = 0.0
    think_time: float = 0.0
    act_time: float = 0.0
    total_time: float = 0.0


class VisionAgent:
    """视觉 GUI 操作 Agent"""

    def __init__(self, config_path: Optional[str] = None, verbose_timing: bool = True):
        self.config = load_config(config_path)
        self.client = OpenAI(
            api_key=self.config["api"]["api_key"],
            base_url=self.config["api"]["base_url"],
        )
        self.model = self.config["api"]["model"]
        self.screen_width = self.config["screen"]["width"]
        self.screen_height = self.config["screen"]["height"]
        self.executor = ActionExecutor()

        agent_config = self.config.get("agent", {})
        self.max_steps = agent_config.get("max_steps", 50)
        self.max_retries = agent_config.get("max_retries", 3)

        safety_config = self.config.get("safety", {})
        self.danger_actions = set(
            safety_config.get(
                "require_confirmation", ["delete", "close", "shutdown", "format"]
            )
        )
        self.auto_confirm_low_risk = safety_config.get("auto_confirm_low_risk", True)

        timing_config = self.config.get("timing", {})
        self.action_delay = timing_config.get("action_delay", 0.5)
        self.screenshot_delay = timing_config.get("screenshot_delay", 1.0)
        self.max_wait_time = timing_config.get("max_wait_time", 10.0)

        self.state = AgentState(max_steps=self.max_steps)
        self.verbose_timing = verbose_timing
        self.step_timing = StepTiming()
        self.total_timing: List[StepTiming] = []

    def _print_timing(self, phase: str, duration: float):
        """打印时间日志"""
        if self.verbose_timing:
            print(f"[耗时] {phase}: {duration:.2f}s")

    def execute(self, instruction: str, auto_confirm: bool = False) -> Dict[str, Any]:
        """
        执行 GUI 操作任务

        Args:
            instruction: 用户指令
            auto_confirm: 是否自动确认所有操作

        Returns:
            执行结果
        """
        import time as t

        task_start = t.time()
        print(f"[任务] {instruction}")

        while self.state.current_step < self.state.max_steps:
            step_start = t.time()
            self.state.current_step += 1
            print(f"\n--- 步骤 {self.state.current_step} ---")

            # 观察阶段
            observe_start = t.time()
            screenshot_b64 = self._observe()
            observe_time = t.time() - observe_start
            self._print_timing("截图", observe_time)

            # 思考阶段
            think_start = t.time()
            action = self._think(screenshot_b64, instruction)
            think_time = t.time() - think_start
            self._print_timing("模型思考", think_time)

            if action.type == ActionType.DONE:
                total_time = t.time() - step_start
                self._print_timing("本步总计", total_time)
                print("\n[统计] ========== 时间统计 ==========")
                for i, timing in enumerate(self.total_timing, 1):
                    print(
                        f"  步骤{i}: 截图={timing.observe_time:.2f}s + 思考={timing.think_time:.2f}s + 执行={timing.act_time:.2f}s = {timing.total_time:.2f}s"
                    )
                print(f"  总计: {t.time() - task_start:.2f}s")
                print("[完成] 任务已完成")
                return {"success": True, "steps": self.state.current_step}

            if action.type == ActionType.WAIT:
                time.sleep(action.x or 1)
                continue

            if not auto_confirm and self._needs_confirmation(action):
                if not self._confirm_action(action):
                    print("[取消] 用户取消操作")
                    return {"success": False, "reason": "user_cancelled"}

            # 执行阶段
            act_start = t.time()
            self._act(action)
            act_time = t.time() - act_start
            self._print_timing("执行操作", act_time)

            if action.type in {ActionType.CLICK, ActionType.DOUBLE_CLICK}:
                time.sleep(self.action_delay)
                self._print_timing("等待渲染", self.action_delay)

            # 记录本步时间
            total_time = t.time() - step_start
            self._print_timing("本步总计", total_time)

            timing = StepTiming(
                observe_time=observe_time,
                think_time=think_time,
                act_time=act_time,
                total_time=total_time,
            )
            self.total_timing.append(timing)

        print("[警告] 达到最大步骤限制")
        return {"success": False, "reason": "max_steps_reached"}

    def _observe(self) -> str:
        """截图观察当前界面"""
        print("[观察] 截取屏幕...")
        screenshot = capture_screen()
        self.state.last_screenshot = image_to_base64(screenshot)
        return self.state.last_screenshot

    def _think(self, screenshot_b64: str, instruction: str) -> Action:
        """思考下一步操作"""
        print("[思考] 分析界面...")

        history_context = self._build_history_context()
        system_context = self._build_system_context()

        prompt = f"""你是一个 GUI 操作助手。请分析当前屏幕截图，根据用户指令决定下一步操作。

## 系统环境
{system_context}

## 用户指令
{instruction}

## 操作历史
{history_context}

## 响应格式
请返回以下 JSON 格式:
{{
    "reasoning": "分析当前界面状态，解释你的决策",
    "action": "click|double_click|right_click|type|drag|scroll|wait|hotkey|done",
    "coordinates": [y, x],  // 1000x1000 归一化坐标，done/wait/hotkey 时可为 null
    "text": "要输入的文本或快捷键",
    "scroll_direction": "up|down|left|right，仅 scroll 操作需要"
}}

## 注意事项
1. 坐标是 [y, x] 格式，范围 0-1000
2. 如果任务已完成，action 设为 "done"
3. 如果需要等待界面加载，action 设为 "wait"，coordinates 设为等待秒数
4. 优先使用配置的快捷键执行操作
5. 避免点击屏幕边缘角落（可能触发安全机制）"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot_b64}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=500,
        )

        result = self._parse_response(response.choices[0].message.content)

        action = Action(
            type=ActionType(result.get("action", "done")),
            reasoning=result.get("reasoning"),
        )

        if "coordinates" in result and result["coordinates"]:
            norm_y, norm_x = result["coordinates"]
            action.x, action.y = normalize_to_pixel(
                norm_y, norm_x, self.screen_width, self.screen_height
            )

        if "text" in result:
            action.text = result["text"]

        self.state.history.append(action)
        print(f"[决策] {action.reasoning}")
        print(
            f"[操作] {action.type.value}"
            + (f" at ({action.x}, {action.y})" if action.x and action.y else "")
        )

        return action

    def _act(self, action: Action) -> None:
        """执行操作"""
        print(f"[执行] {action.type.value}...")

        if action.type == ActionType.CLICK:
            self.executor.click(action.x, action.y)
        elif action.type == ActionType.DOUBLE_CLICK:
            self.executor.double_click(action.x, action.y)
        elif action.type == ActionType.RIGHT_CLICK:
            self.executor.right_click(action.x, action.y)
        elif action.type == ActionType.TYPE:
            if action.text:
                if any("\u4e00" <= c <= "\u9fff" for c in action.text):
                    self.executor.type_chinese(action.text)
                else:
                    self.executor.type_text(action.text)
        elif action.type == ActionType.DRAG:
            if action.x and action.y:
                self.executor.drag(
                    (action.x, action.y), (action.x + 100, action.y + 100)
                )
        elif action.type == ActionType.SCROLL:
            if action.text:
                self.executor.scroll(action.text)
        elif action.type == ActionType.HOTKEY:
            if action.text:
                keys = action.text.split("+")
                self.executor.hotkey(*keys)

    def _build_history_context(self) -> str:
        """构建历史上下文"""
        if not self.state.history:
            return "无历史操作"

        lines = []
        for i, action in enumerate(self.state.history[-5:], 1):
            lines.append(f"{i}. {action.type.value}: {action.reasoning or 'N/A'}")
        return "\n".join(lines)

    def _build_system_context(self) -> str:
        """构建系统环境上下文"""
        config = self.config.get("system_prompt", {})

        if not config.get("enabled", True):
            return "未配置"

        lines = []

        os_info = config.get("os", "Unknown")
        desktop = config.get("desktop", "Unknown")
        language = config.get("language", "en_US")
        lines.append(f"- 操作系统: {os_info}")
        lines.append(f"- 桌面环境: {desktop}")
        lines.append(f"- 界面语言: {language}")

        shortcuts = config.get("custom_shortcuts", {})
        if shortcuts:
            lines.append("\n### 可用快捷键")
            for name, key in shortcuts.items():
                desc = {
                    "show_desktop": "显示桌面",
                    "open_terminal": "打开终端",
                    "switch_window": "切换窗口",
                    "close_window": "关闭窗口",
                    "open_file_manager": "打开文件管理器",
                }.get(name, name)
                lines.append(f"- {desc}: {key}")

        custom_instructions = config.get("custom_instructions", "")
        if custom_instructions:
            lines.append(f"\n### 自定义说明\n{custom_instructions}")

        return "\n".join(lines)

    def _parse_response(self, content: str) -> Dict:
        """解析模型响应"""
        import json
        import re

        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            return json.loads(json_match.group())
        return {"action": "done"}

    def _needs_confirmation(self, action: Action) -> bool:
        """判断是否需要确认"""
        if action.type.value in self.danger_actions:
            return True
        return not self.auto_confirm_low_risk

    def _confirm_action(self, action: Action) -> bool:
        """请求用户确认"""
        print(f"\n[确认] 即将执行: {action.type.value}")
        if action.x and action.y:
            print(f"        坐标: ({action.x}, {action.y})")
        if action.text:
            print(f"        内容: {action.text}")

        response = input("        确认执行? [y/N]: ").strip().lower()
        return response == "y"

    def reset(self) -> None:
        """重置 Agent 状态"""
        self.state = AgentState(max_steps=self.max_steps)
        self.total_timing = []
        print("[重置] Agent 状态已清空")


def main():
    """交互式入口"""
    import argparse

    parser = argparse.ArgumentParser(description="视觉 GUI 操作 Agent")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--auto", action="store_true", help="自动确认所有操作")
    parser.add_argument("--quiet", action="store_true", help="不显示时间日志")
    args = parser.parse_args()

    agent = VisionAgent(args.config, verbose_timing=not args.quiet)

    print("视觉 GUI 操作 Agent")
    print("输入指令开始操作，输入 'quit' 退出\n")

    while True:
        try:
            instruction = input("指令> ").strip()
            if instruction.lower() == "quit":
                break
            if not instruction:
                continue

            agent.reset()
            result = agent.execute(instruction, auto_confirm=args.auto)
            print(f"\n结果: {result}")

        except KeyboardInterrupt:
            print("\n[中断] 操作已取消")
            agent.reset()
        except Exception as e:
            print(f"[错误] {e}")


if __name__ == "__main__":
    main()
