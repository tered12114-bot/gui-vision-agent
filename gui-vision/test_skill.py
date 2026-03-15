"""
Skill 测试脚本 - 验证代码逻辑
"""

import sys

sys.path.insert(0, "/home/xiaotian/桌面/work/vision_agent/gui-vision")

from scripts.utils import load_config, normalize_to_pixel, validate_coordinates
from scripts.vision import capture_screen, image_to_base64
from scripts.action import ActionExecutor, ActionType
from scripts.agent import Action, AgentState


def test_utils():
    """测试工具函数"""
    print("\n=== 测试 utils 模块 ===")

    # 测试坐标转换
    x, y = normalize_to_pixel(500, 500, 1920, 1080)
    assert x == 960 and y == 540, f"坐标转换错误: ({x}, {y})"
    print("✓ 坐标转换正确")

    # 测试边界情况
    x, y = normalize_to_pixel(0, 0, 1920, 1080)
    assert x == 0 and y == 0, f"左上角转换错误: ({x}, {y})"
    print("✓ 左上角转换正确")

    x, y = normalize_to_pixel(1000, 1000, 1920, 1080)
    assert x == 1919 and y == 1079, f"右下角转换错误: ({x}, {y})"
    print("✓ 右下角转换正确")

    # 测试坐标验证
    assert validate_coordinates(100, 100, 1920, 1080) == True
    assert validate_coordinates(2000, 100, 1920, 1080) == False
    print("✓ 坐标验证正确")

    # 测试配置加载
    config = load_config()
    assert "api" in config
    assert "screen" in config
    print(
        f"✓ 配置加载成功，屏幕尺寸: {config['screen']['width']}x{config['screen']['height']}"
    )


def test_vision():
    """测试视觉模块"""
    print("\n=== 测试 vision 模块 ===")

    # 测试截图
    screenshot = capture_screen()
    assert screenshot is not None
    print(f"✓ 截图成功，尺寸: {screenshot.size}")

    # 测试 base64 转换
    b64 = image_to_base64(screenshot)
    assert len(b64) > 0
    print(f"✓ Base64 转换成功，长度: {len(b64)}")


def test_action():
    """测试动作模块"""
    print("\n=== 测试 action 模块 ===")

    executor = ActionExecutor()

    # 测试获取鼠标位置
    pos = executor.get_position()
    assert pos is not None
    print(f"✓ 鼠标位置: {pos}")

    # 测试动作类型
    assert ActionType.CLICK.value == "click"
    assert ActionType.DOUBLE_CLICK.value == "double_click"
    print("✓ 动作类型枚举正确")


def test_agent_state():
    """测试 Agent 状态"""
    print("\n=== 测试 agent 状态 ===")

    state = AgentState()
    assert len(state.history) == 0
    assert state.current_step == 0
    assert state.max_steps == 50
    print("✓ Agent 状态初始化正确")

    # 测试添加历史记录
    action = Action(type=ActionType.CLICK, x=100, y=200, reasoning="测试点击")
    state.history.append(action)
    assert len(state.history) == 1
    print("✓ 历史记录添加成功")


def test_agent_config():
    """测试 Agent 配置"""
    print("\n=== 测试 Agent 配置 ===")

    config = load_config()

    # 检查 API 配置
    assert config["api"]["base_url"] != ""
    assert config["api"]["model"] == "qwen-3.5-plus"
    print(f"✓ API 配置正确")
    print(f"  - Base URL: {config['api']['base_url']}")
    print(f"  - Model: {config['api']['model']}")

    # 检查安全配置
    assert "auto_confirm_low_risk" in config["safety"]
    print(f"✓ 安全配置正确")


def main():
    print("=" * 50)
    print("GUI Vision Skill 测试")
    print("=" * 50)

    try:
        test_utils()
        test_vision()
        test_action()
        test_agent_state()
        test_agent_config()

        print("\n" + "=" * 50)
        print("所有测试通过! ✓")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
