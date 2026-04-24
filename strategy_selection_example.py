"""
策略选择示例 - 展示多智能体如何根据上下文选择策略
"""
import asyncio
from strategy_manager import StrategyManager
from models import UserInput, EmotionType, StageType, IntensityType, RiskType


async def demo_strategy_selection():
    """演示不同场景下的策略选择"""
    
    manager = StrategyManager(use_llm_agent=False)  # 使用规则模式演示
    
    # 测试场景列表
    test_cases = [
        {
            "name": "场景 1: 高风险情况",
            "input": UserInput(
                text="我真的不想活了，活着太累了",
                emotion=EmotionType.SAD,
                stage=StageType.VENTING,
                intensity=IntensityType.HIGH,
                risk=RiskType.HIGH
            ),
            "expected": "SAFETY"
        },
        {
            "name": "场景 2: 悲伤发泄（高强度）",
            "input": UserInput(
                text="我付出了那么多，为什么结果是这样！我真的好不甘心！",
                emotion=EmotionType.SAD,
                stage=StageType.VENTING,
                intensity=IntensityType.HIGH,
                risk=RiskType.LOW
            ),
            "expected": "VENTING_SUPPORT"
        },
        {
            "name": "场景 3: 焦虑求助（高密度）",
            "input": UserInput(
                text="我最近总是心慌，睡不好，我该怎么办？",
                emotion=EmotionType.ANXIOUS,
                stage=StageType.HELP,
                intensity=IntensityType.HIGH,
                risk=RiskType.LOW
            ),
            "expected": "BREATHING"
        },
        {
            "name": "场景 4: 愤怒共情",
            "input": UserInput(
                text="他们怎么能这样对我？我太生气了！",
                emotion=EmotionType.ANGRY,
                stage=StageType.VENTING,
                intensity=IntensityType.MEDIUM,
                risk=RiskType.LOW
            ),
            "expected": "EMPATHY"
        },
        {
            "name": "场景 5: 积极情绪",
            "input": UserInput(
                text="今天孙子来看我了，我好开心！",
                emotion=EmotionType.POSITIVE,
                stage=StageType.NEUTRAL,
                intensity=IntensityType.HIGH,
                risk=RiskType.LOW
            ),
            "expected": "JOY_SHARE"
        },
        {
            "name": "场景 6: 日常陪伴",
            "input": UserInput(
                text="今天天气不错，你吃饭了吗？",
                emotion=EmotionType.NEUTRAL,
                stage=StageType.NEUTRAL,
                intensity=IntensityType.LOW,
                risk=RiskType.LOW
            ),
            "expected": "COMPANY"
        },
        {
            "name": "场景 7: 求助 - 睡眠问题",
            "input": UserInput(
                text="最近总是失眠，有什么办法吗？",
                emotion=EmotionType.ANXIOUS,
                stage=StageType.HELP,
                intensity=IntensityType.MEDIUM,
                risk=RiskType.LOW
            ),
            "expected": "GUIDANCE_LIGHT"
        },
        {
            "name": "场景 8: 焦虑（中强度）",
            "input": UserInput(
                text="我总是担心这个担心那个，心里不踏实",
                emotion=EmotionType.ANXIOUS,
                stage=StageType.VENTING,
                intensity=IntensityType.MEDIUM,
                risk=RiskType.LOW
            ),
            "expected": "BREATHING"
        },
        {
            "name": "场景 9: 悲伤（低强度）",
            "input": UserInput(
                text="最近有点失落，提不起精神",
                emotion=EmotionType.SAD,
                stage=StageType.VENTING,
                intensity=IntensityType.LOW,
                risk=RiskType.LOW
            ),
            "expected": "MUSIC_OFFER"
        },
        {
            "name": "场景 10: 求助 - 缺乏动力",
            "input": UserInput(
                text="我什么都不想做，每天很无聊",
                emotion=EmotionType.SAD,
                stage=StageType.HELP,
                intensity=IntensityType.LOW,
                risk=RiskType.LOW
            ),
            "expected": "INTEREST_REDIRECT"
        }
    ]
    
    print("=" * 60)
    print("策略选择演示")
    print("=" * 60)
    
    for case in test_cases:
        print(f"\n{case['name']}")
        print(f"输入：{case['input'].text}")
        print(f"情绪：{case['input'].emotion.value} | "
              f"状态：{case['input'].stage.value} | "
              f"强度：{case['input'].intensity.value} | "
              f"风险：{case['input'].risk.value}")
        
        # 创建状态判断
        from models import StateJudgment
        state = StateJudgment(
            stage=case['input'].stage,
            intensity=case['input'].intensity,
            risk=case['input'].risk
        )
        
        # 选择策略
        response = await manager.select_and_execute(
            user_input=case['input'],
            state=state,
            session_id="demo_session"
        )
        
        print(f"选择策略：{response.strategy}")
        print(f"预期策略：{case['expected']}")
        print(f"匹配：{'✓' if response.strategy == case['expected'] else '✗'}")
        print(f"回复预览：{response.response_text[:100]}...")
        print("-" * 60)


def demo_strategy_info():
    """演示获取策略信息"""
    manager = StrategyManager(use_llm_agent=False)
    
    print("\n" + "=" * 60)
    print("策略信息展示（供智能体使用）")
    print("=" * 60)
    
    strategies_info = manager.get_strategy_for_agent()
    
    for strategy in strategies_info:
        print(f"\n【{strategy['name']}】")
        print(f"描述：{strategy['description']}")
        print(f"适用条件:")
        print(f"  - 情绪：{strategy['suitable_for']['emotions']}")
        print(f"  - 状态：{strategy['suitable_for']['stages']}")
        print(f"  - 强度：{strategy['suitable_for']['intensities']}")
        print(f"  - 风险：{strategy['suitable_for']['risks']}")
        print(f"可用方法：{strategy['available_methods']}")


async def main():
    """主函数"""
    # 演示策略信息
    demo_strategy_info()
    
    # 演示策略选择
    await demo_strategy_selection()
    
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())