"""
LLM 服务封装
"""
from typing import Optional, Dict, Any
import httpx
from loguru import logger
from pathlib import Path

from models import StateJudgment, StageType, IntensityType, RiskType, EmotionType
from config import get_settings


class LLMService:
    """LLM 服务基类"""
    
    def __init__(self, api_key: str = None, api_base_url: str = None, model: str = None):
        settings = get_settings()
        self.api_key = api_key or settings.SILICONFLOW_API_KEY
        self.api_base_url = api_base_url or settings.SILICONFLOW_API_BASE_URL
        self.model = model or settings.SILICONFLOW_MODEL
        self.timeout = 30.0
    
    async def _call_llm(self, messages: list[dict], temperature: float = 0.7) -> str:
        """调用 LLM API"""
        if not self.api_key:
            raise ValueError("API Key 未配置")
        
        url = f"{self.api_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1024
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]


class StateAnalysisAgent(LLMService):
    """状态分析智能体 - 分析用户的情绪状态、强度、风险等"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "StateAnalysisAgent"
    
    async def analyze(self, text: str, emotion: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> StateJudgment:
        """
        分析用户状态
        
        Args:
            text: 用户输入文本
            emotion: 初步识别的情绪（可选）
            context: 上下文信息（可选）
        
        Returns:
            StateJudgment: 状态判断结果
        """
        system_prompt = """你是一个专业的情感陪伴状态分析专家。你的任务是分析用户的心理状态，包括：
1. stage（状态阶段）：venting（情绪发泄）、help（寻求帮助）、neutral（自然交流）
2. intensity（情绪强度）：low（低）、medium（中）、high（高）
3. risk（风险等级）：low（低风险）、high（高风险，如有自伤自杀倾向）

请根据用户的表达内容、语气、用词等进行综合判断。

输出格式（严格 JSON）：
{
    "stage": "venting|help|neutral",
    "intensity": "low|medium|high",
    "risk": "low|high",
    "reasoning": "简要分析理由"
}"""
        
        user_prompt = f"用户输入：{text}\n"
        if emotion:
            user_prompt += f"初步情绪识别：{emotion}\n"
        if context:
            user_prompt += f"上下文信息：{context}\n"
        user_prompt += "\n请分析用户的状态。"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._call_llm(messages, temperature=0.3)
            import json
            # 尝试提取 JSON
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
            else:
                result = json.loads(response)
            
            return StateJudgment(
                stage=StageType(result.get("stage", "neutral")),
                intensity=IntensityType(result.get("intensity", "low")),
                risk=RiskType(result.get("risk", "low"))
            )
        except Exception as e:
            logger.error(f"[{self.name}] 分析失败：{e}")
            # Fallback 到默认状态
            return StateJudgment(
                stage=StageType.NEUTRAL,
                intensity=IntensityType.LOW,
                risk=RiskType.LOW
            )


class EmotionAnalysisAgent(LLMService):
    """情绪分析智能体 - 深度分析用户的情绪类型"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "EmotionAnalysisAgent"
    
    async def analyze(self, text: str, context: Optional[Dict[str, Any]] = None) -> EmotionType:
        """
        分析用户情绪
        
        Args:
            text: 用户输入文本
            context: 上下文信息（可选）
        
        Returns:
            EmotionType: 情绪类型
        """
        system_prompt = """你是一个专业的情绪分析专家。请分析用户的情绪状态。

可选情绪类型：
- sad: 悲伤、难过、失落
- angry: 愤怒、生气、不满
- anxious: 焦虑、紧张、担忧
- neutral: 平静、中性
- positive: 开心、喜悦、积极

输出格式（严格 JSON）：
{
    "emotion": "sad|angry|anxious|neutral|positive",
    "confidence": 0.0-1.0,
    "reasoning": "简要分析理由"
}"""
        
        user_prompt = f"用户输入：{text}\n"
        if context:
            user_prompt += f"上下文信息：{context}\n"
        user_prompt += "\n请分析用户的主要情绪。"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._call_llm(messages, temperature=0.3)
            import json
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
            else:
                result = json.loads(response)
            
            emotion_str = result.get("emotion", "neutral")
            return EmotionType(emotion_str)
        except Exception as e:
            logger.error(f"[{self.name}] 情绪分析失败：{e}")
            return EmotionType.NEUTRAL


class StrategySelectionAgent(LLMService):
    """策略选择智能体 - 根据状态和情绪选择合适的策略"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "StrategySelectionAgent"
    
    async def select(
        self,
        text: str,
        emotion: EmotionType,
        state: StateJudgment,
        available_strategies: list[dict]
    ) -> str:
        """
        选择合适的策略
        
        Args:
            text: 用户输入文本
            emotion: 情绪类型
            state: 状态判断
            available_strategies: 可用策略列表（包含 suitable_for 和 available_methods）
        
        Returns:
            str: 选中的策略名称
        """
        strategies_info = "\n".join([
            f"- {s['name']}: {s['description']}\n"
            f"  适用：情绪={s['suitable_for']['emotions']}, 状态={s['suitable_for']['stages']}, "
            f"强度={s['suitable_for']['intensities']}, 风险={s['suitable_for']['risks']}\n"
            f"  可用方法：{s['available_methods']}"
            for s in available_strategies
        ])
        
        system_prompt = f"""你是一个情感陪伴策略选择专家。根据用户的状态和情绪，选择最合适的陪伴策略。

可用策略信息：
{strategies_info}

选择原则：
1. 【高风险】risk=high 时，必须选择 SAFETY（安全干预）
2. 【发泄状态】stage=venting 时：
   - 高强度：VENTING_SUPPORT（倾诉引导）或 EMPATHY（共情）
   - 中低强度：MUSIC_OFFER（音乐推荐）
3. 【求助状态】stage=help 时：
   - 高强度：GUIDANCE_LIGHT（温和建议）+ BREATHING（呼吸练习）
   - 中低强度：INTEREST_REDIRECT（兴趣转移）
4. 【积极情绪】emotion=positive 时：
   - JOY_SHARE（喜悦分享）或 MUSIC_OFFER（音乐推荐）
5. 【中性情绪】emotion=neutral 且 stage=neutral 时：
   - COMPANY（日常陪伴）或 INTEREST_REDIRECT（兴趣转移）
6. 【焦虑情绪】emotion=anxious 且强度>=medium 时：
   - BREATHING（呼吸练习）优先

输出格式（严格 JSON）：
{{
    "strategy": "策略名称",
    "reasoning": "选择理由，说明匹配的条件和策略功能"
}}"""
        
        user_prompt = f"""用户输入：{text}
情绪：{emotion.value}
状态阶段：{state.stage.value}
情绪强度：{state.intensity.value}
风险等级：{state.risk.value}

请根据策略适用条件选择最匹配的策略。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._call_llm(messages, temperature=0.5)
            import json
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
            else:
                result = json.loads(response)
            
            return result.get("strategy", "EMPATHY")
        except Exception as e:
            logger.error(f"[{self.name}] 策略选择失败：{e}")
            return "EMPATHY"  # Fallback 到共情策略


class ResponseGenerationAgent(LLMService):
    """响应生成智能体 - 生成具体的回复内容"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ResponseGenerationAgent"
    
    async def generate(
        self,
        text: str,
        emotion: EmotionType,
        state: StateJudgment,
        strategy_name: str,
        method_results: list,
        conversation_history: Optional["ConversationHistory"] = None
    ) -> str:
        """
        生成最终回复
        
        Args:
            text: 用户输入文本
            emotion: 情绪类型
            state: 状态判断
            strategy_name: 策略名称
            method_results: 策略方法执行结果
            conversation_history: 对话历史（可选）
        
        Returns:
            str: 最终回复文本
        """
        methods_info = "\n".join([
            f"- {m['method_name']}: {m['content']}"
            for m in method_results
        ])
        
        # 构建对话历史上下文
        history_context = ""
        if conversation_history and conversation_history.messages:
            history_context = conversation_history.to_llm_format(limit=10)
        
        system_prompt = f"""你是一个温暖、专业的情感陪伴助手。请根据策略执行结果，生成自然、真诚的回复。

回复原则：
1. 语气温暖、亲切，像朋友一样交流
2. 避免说教，多表达理解和陪伴
3. 根据用户情绪调整语气（悲伤时温柔，焦虑时安抚，开心时分享）
4. 回复长度适中，不要过于冗长
5. 可以适当使用策略提供的话术，但要自然融入
6. **重要**：参考对话历史，保持上下文连贯性，不要重复之前说过的话
7. 如果用户提到之前聊过的内容，要能接上话题

策略执行的方法和内容：
{methods_info}

请生成最终回复。"""
        
        user_prompt = f"""用户输入：{text}
用户情绪：{emotion.value}
用户状态：{state.stage.value}
使用策略：{strategy_name}"""
        
        if history_context:
            user_prompt += f"""

之前的对话：
{history_context}"""
        
        user_prompt += """

请根据以上信息和方法内容，生成自然、温暖的回复。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._call_llm(messages, temperature=0.7)
            return response.strip()
        except Exception as e:
            logger.error(f"[{self.name}] 响应生成失败：{e}")
            # Fallback 返回第一个方法的内容
            if method_results:
                return method_results[0].get("content", "我在这里陪着你")
            return "我在这里陪着你，想聊什么都可以。"


class AgentOrchestrator:
    """智能体编排器 - 协调多个智能体完成情感陪伴任务"""
    
    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        self.state_agent = StateAnalysisAgent(api_key=api_key, model=model, **kwargs)
        self.emotion_agent = EmotionAnalysisAgent(api_key=api_key, model=model, **kwargs)
        self.strategy_agent = StrategySelectionAgent(api_key=api_key, model=model, **kwargs)
        self.response_agent = ResponseGenerationAgent(api_key=api_key, model=model, **kwargs)
        logger.info("[AgentOrchestrator] 智能体编排器初始化完成")
    
    async def process(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        available_strategies: Optional[list[dict]] = None,
        conversation_history: Optional["ConversationHistory"] = None
    ) -> Dict[str, Any]:
        """
        处理用户输入，协调各智能体完成分析和响应
        
        Args:
            text: 用户输入文本
            context: 上下文信息
            available_strategies: 可用策略列表
            conversation_history: 对话历史（可选）
        
        Returns:
            Dict: 包含所有分析结果和最终响应
        """
        logger.info(f"[AgentOrchestrator] 开始处理 | 文本：{text[:50]}...")
        
        # 构建上下文信息
        ctx_info = context or {}
        if conversation_history and conversation_history.messages:
            history_context = conversation_history.to_llm_format(limit=10)
            if history_context:
                ctx_info["conversation_history"] = history_context
        
        # 1. 情绪分析（考虑上下文）
        emotion = await self.emotion_agent.analyze(text, ctx_info)
        logger.info(f"[AgentOrchestrator] 情绪分析完成：{emotion.value}")
        
        # 2. 状态分析（考虑上下文）
        state = await self.state_agent.analyze(text, emotion.value, ctx_info)
        logger.info(f"[AgentOrchestrator] 状态分析完成 | 阶段：{state.stage.value} | 强度：{state.intensity.value} | 风险：{state.risk.value}")
        
        # 3. 策略选择（如果有策略列表）
        strategy_name = "EMPATHY"
        if available_strategies:
            strategy_name = await self.strategy_agent.select(text, emotion, state, available_strategies)
            logger.info(f"[AgentOrchestrator] 策略选择完成：{strategy_name}")
        
        return {
            "emotion": emotion,
            "state": state,
            "selected_strategy": strategy_name
        }