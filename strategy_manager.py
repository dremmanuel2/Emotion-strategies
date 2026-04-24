"""
策略管理器 - 根据状态选择合适的策略
"""
from typing import List, Type, Optional, Dict, Any
from loguru import logger
import uuid
from datetime import datetime

from models import (
    UserInput, StrategyResponse, StateJudgment,
    ConversationHistory, ChatMessage
)
from strategies.base import BaseStrategy
from strategies.safety import SafetyStrategy
from strategies.empathy import EmpathyStrategy
from strategies.venting import VentingSupportStrategy
from strategies.guidance import GuidanceLightStrategy
from strategies.breathing import BreathingStrategy
from strategies.music import MusicOfferStrategy
from strategies.interest import InterestRedirectStrategy
from strategies.joy import JoyShareStrategy
from strategies.company import CompanyStrategy
from llm_agents import AgentOrchestrator


class StrategyManager:
    """策略管理器"""
    
    def __init__(self, use_llm_agent: bool = True, api_key: str = None):
        # 策略列表
        self.strategies: List[BaseStrategy] = [
            SafetyStrategy(),
            EmpathyStrategy(),
            VentingSupportStrategy(),
            BreathingStrategy(),
            GuidanceLightStrategy(),
            MusicOfferStrategy(),
            InterestRedirectStrategy(),
            JoyShareStrategy(),
            CompanyStrategy(),
        ]
        
        # 是否使用 LLM 智能体进行策略选择
        self.use_llm_agent = use_llm_agent
        self.agent_orchestrator = None
        
        if use_llm_agent:
            try:
                self.agent_orchestrator = AgentOrchestrator(api_key=api_key)
                logger.info("[StrategyManager] LLM 智能体编排器初始化完成")
            except Exception as e:
                logger.warning(f"[StrategyManager] LLM 智能体初始化失败，使用规则模式：{e}")
                self.use_llm_agent = False
        
        # 对话历史管理
        self.conversations: Dict[str, ConversationHistory] = {}
        logger.info(f"[StrategyManager] 初始化完成，加载 {len(self.strategies)} 个策略 | 模式：{'LLM 智能体' if use_llm_agent else '规则'}")
    
    def get_or_create_conversation(self, session_id: str = None) -> ConversationHistory:
        """获取或创建对话历史"""
        if not session_id or session_id not in self.conversations:
            session_id = session_id or str(uuid.uuid4())
            now = datetime.now().isoformat()
            self.conversations[session_id] = ConversationHistory(
                session_id=session_id,
                created_at=now,
                updated_at=now,
                max_messages=20
            )
            logger.info(f"[StrategyManager] 创建新会话：{session_id}")
        
        return self.conversations[session_id]
    
    def add_to_history(
        self,
        session_id: str,
        role: str,
        content: str,
        emotion: str = None,
        strategy: str = None
    ):
        """添加消息到对话历史"""
        conversation = self.get_or_create_conversation(session_id)
        conversation.add_message(role, content, emotion, strategy)
    
    def get_history(self, session_id: str) -> Optional[ConversationHistory]:
        """获取对话历史"""
        return self.conversations.get(session_id)
    
    async def select_and_execute(
        self,
        user_input: UserInput,
        state: StateJudgment,
        session_id: str = None
    ) -> StrategyResponse:
        """
        选择并执行合适的策略
        
        Args:
            user_input: 用户输入
            state: 状态判断结果
            session_id: 会话 ID（用于上下文）
        
        Returns:
            StrategyResponse: 策略响应
        """
        logger.info(
            f"[StrategyManager] 开始选择策略 | "
            f"情绪：{user_input.emotion.value} | "
            f"状态：{state.stage.value} | "
            f"强度：{state.intensity.value} | "
            f"风险：{state.risk.value} | "
            f"模式：{'LLM 智能体' if self.use_llm_agent else '规则'}"
        )
        
        # 获取对话历史
        conversation = self.get_or_create_conversation(session_id) if session_id else None
        
        selected_strategy_name = None
        
        # 使用 LLM 智能体选择策略
        if self.use_llm_agent and self.agent_orchestrator:
            try:
                # 获取详细的策略信息（包含适用条件和方法列表）
                strategies_info = self.get_strategy_for_agent()
                
                agent_result = await self.agent_orchestrator.process(
                    text=user_input.text,
                    emotion=user_input.emotion.value,
                    state=state,
                    available_strategies=strategies_info,
                    conversation_history=conversation
                )
                selected_strategy_name = agent_result.get("selected_strategy")
                logger.info(f"[StrategyManager] LLM 智能体选择策略：{selected_strategy_name}")
            except Exception as e:
                logger.warning(f"[StrategyManager] LLM 智能体选择失败，回退到规则模式：{e}")
        
        # 规则模式：按优先级检查策略
        if not selected_strategy_name:
            for strategy in self.strategies:
                if strategy.can_handle(user_input, state):
                    selected_strategy_name = strategy.name
                    logger.info(f"[StrategyManager] 规则模式选择策略：{strategy.name}")
                    break
        
        # 执行选中的策略
        if selected_strategy_name:
            for strategy in self.strategies:
                if strategy.name == selected_strategy_name:
                    try:
                        response = await strategy.execute(user_input, state)
                        logger.info(f"[StrategyManager] 策略执行成功：{strategy.name}")
                        return response
                    except Exception as e:
                        logger.error(f"[StrategyManager] 策略执行失败：{strategy.name}, 错误：{e}")
                        # 继续尝试下一个策略
                        continue
        
        # 如果没有策略匹配，返回默认共情响应
        logger.warning("[StrategyManager] 没有匹配的策略，使用默认共情")
        return await self._default_response(user_input, state)
    
    async def _default_response(self, user_input: UserInput, state: StateJudgment) -> StrategyResponse:
        """默认响应"""
        from models import MethodResult
        
        methods = [
            MethodResult(
                method_name="默认共情",
                content="我能理解你现在的感受。我在这儿陪着你，你想聊什么都可以。"
            )
        ]
        
        return StrategyResponse(
            strategy="DEFAULT_EMPATHY",
            methods=methods,
            response_text=methods[0].content,
            metadata={"fallback": True}
        )
    
    def get_strategy_info(self) -> List[dict]:
        """获取所有策略信息（包含详细元数据）"""
        return [
            {
                "name": s.name,
                "description": s.description,
                "class": s.__class__.__name__,
                "suitable_emotions": s.suitable_emotions,
                "suitable_stages": s.suitable_stages,
                "suitable_intensities": s.suitable_intensities,
                "suitable_risks": s.suitable_risks,
                "methods_info": s.methods_info
            }
            for s in self.strategies
        ]
    
    def get_strategy_for_agent(self) -> List[dict]:
        """获取适合智能体读取的策略信息（精简版）"""
        return [
            {
                "name": s.name,
                "description": s.description,
                "suitable_for": {
                    "emotions": s.suitable_emotions,
                    "stages": s.suitable_stages,
                    "intensities": s.suitable_intensities,
                    "risks": s.suitable_risks
                },
                "available_methods": [m["name"] for m in s.methods_info]
            }
            for s in self.strategies
        ]