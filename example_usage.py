"""
智能体系统使用示例

展示如何使用多智能体系统进行情感分析
"""
import asyncio
from llm_agents import (
    AgentOrchestrator,
    EmotionAnalysisAgent,
    StateAnalysisAgent,
    StrategySelectionAgent,
    ResponseGenerationAgent
)


async def example_single_agent():
    """示例 1: 使用单个智能体"""
    print("="*60)
    print("示例 1: 使用单个智能体")
    print("="*60)
    
    # 创建情绪分析智能体
    emotion_agent = EmotionAnalysisAgent()
    
    text = "我今天心情很糟糕，什么都不想做"
    
    # 分析情绪
    emotion = await emotion_agent.analyze(text)
    print(f"\n输入：{text}")
    print(f"分析情绪：{emotion.value}")
    
    # 创建状态分析智能体
    state_agent = StateAnalysisAgent()
    
    # 分析状态
    state = await state_agent.analyze(text, emotion.value)
    print(f"\n状态分析:")
    print(f"  阶段：{state.stage.value}")
    print(f"  强度：{state.intensity.value}")
    print(f"  风险：{state.risk.value}")


async def example_orchestrator():
    """示例 2: 使用智能体编排器"""
    print("\n" + "="*60)
    print("示例 2: 使用智能体编排器")
    print("="*60)
    
    text = "最近总是失眠，感觉很焦虑，不知道该怎么办"
    
    # 创建编排器
    orchestrator = AgentOrchestrator()
    
    # 准备策略列表
    strategies_info = [
        {"name": "SafetyStrategy", "description": "安全干预（高风险情况）"},
        {"name": "EmpathyStrategy", "description": "共情陪伴"},
        {"name": "BreathingStrategy", "description": "呼吸引导"},
        {"name": "GuidanceLightStrategy", "description": "轻度建议"},
        {"name": "MusicOfferStrategy", "description": "音乐推荐"},
    ]
    
    # 执行完整分析流程
    result = await orchestrator.process(
        text=text,
        available_strategies=strategies_info
    )
    
    print(f"\n输入：{text}")
    print(f"\n分析结果:")
    print(f"  情绪：{result['emotion'].value}")
    print(f"  状态阶段：{result['state'].stage.value}")
    print(f"  状态强度：{result['state'].intensity.value}")
    print(f"  风险等级：{result['state'].risk.value}")
    print(f"  选择策略：{result['selected_strategy']}")


async def example_full_pipeline():
    """示例 3: 完整流程（分析 + 策略执行 + 响应生成）"""
    print("\n" + "="*60)
    print("示例 3: 完整流程")
    print("="*60)
    
    from strategy_manager import StrategyManager
    from models import UserInput
    
    text = "我和老伴吵架了，心里很难受"
    
    # 1. 智能体分析
    orchestrator = AgentOrchestrator()
    strategies_info = [
        {"name": "EmpathyStrategy", "description": "共情陪伴"},
        {"name": "VentingSupportStrategy", "description": "引导倾诉"},
        {"name": "MusicOfferStrategy", "description": "音乐推荐"},
    ]
    
    analysis = await orchestrator.process(
        text=text,
        available_strategies=strategies_info
    )
    
    # 2. 创建策略管理器并执行策略
    strategy_manager = StrategyManager(use_llm_agent=False)  # 已分析过，不需要再次选择
    
    user_input = UserInput(
        text=text,
        emotion=analysis["emotion"]
    )
    
    # 找到并执行选中的策略
    selected_strategy = None
    for strategy in strategy_manager.strategies:
        if strategy.name == analysis["selected_strategy"]:
            selected_strategy = strategy
            break
    
    if selected_strategy:
        response = await selected_strategy.execute(user_input, analysis["state"])
        
        print(f"\n输入：{text}")
        print(f"\n智能体分析:")
        print(f"  情绪：{analysis['emotion'].value}")
        print(f"  状态：{analysis['state'].stage.value}")
        print(f"  策略：{analysis['selected_strategy']}")
        print(f"\n策略回复:")
        print(f"  {response.response_text}")
    else:
        print("未找到合适的策略")


async def example_with_custom_api_key(api_key: str):
    """示例 4: 使用自定义 API Key"""
    print("\n" + "="*60)
    print("示例 4: 使用自定义 API Key")
    print("="*60)
    
    text = "感觉最近压力很大"
    
    # 使用自定义 API Key 创建智能体
    orchestrator = AgentOrchestrator(api_key=api_key)
    
    strategies_info = [
        {"name": "EmpathyStrategy", "description": "共情陪伴"},
        {"name": "BreathingStrategy", "description": "呼吸引导"},
    ]
    
    result = await orchestrator.process(
        text=text,
        available_strategies=strategies_info
    )
    
    print(f"\n输入：{text}")
    print(f"情绪：{result['emotion'].value}")
    print(f"策略：{result['selected_strategy']}")


async def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("多智能体情感陪伴系统 - 使用示例")
    print("="*60 + "\n")
    
    # 注意：运行这些示例需要配置 API Key
    # 方法 1: 在 .env 文件中配置 SILICONFLOW_API_KEY
    # 方法 2: 使用 example_with_custom_api_key("your_api_key")
    
    try:
        # 示例 1: 单个智能体
        await example_single_agent()
    except Exception as e:
        print(f"示例 1 失败：{e}")
    
    try:
        # 示例 2: 智能体编排器
        await example_orchestrator()
    except Exception as e:
        print(f"示例 2 失败：{e}")
    
    try:
        # 示例 3: 完整流程
        await example_full_pipeline()
    except Exception as e:
        print(f"示例 3 失败：{e}")
    
    # 示例 4: 自定义 API Key（需要填入真实的 API Key）
    # await example_with_custom_api_key("your_api_key_here")
    
    print("\n" + "="*60)
    print("示例运行完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())