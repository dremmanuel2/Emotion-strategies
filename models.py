"""
数据模型定义
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EmotionType(str, Enum):
    """情绪类型"""
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class StageType(str, Enum):
    """状态类型"""
    VENTING = "venting"      # 发泄
    HELP = "help"            # 求助
    NEUTRAL = "neutral"      # 自然


class IntensityType(str, Enum):
    """强度类型"""
    LOW = "low"              # 低
    MEDIUM = "medium"        # 中
    HIGH = "high"            # 高


class RiskType(str, Enum):
    """风险类型"""
    LOW = "low"              # 低风险
    HIGH = "high"            # 高风险


class UserInput(BaseModel):
    """用户输入"""
    text: str = Field(..., description="用户输入文本")
    emotion: EmotionType = Field(..., description="识别的情绪类型")
    stage: Optional[StageType] = Field(None, description="状态类型")
    intensity: Optional[IntensityType] = Field(None, description="强度")
    risk: Optional[RiskType] = Field(None, description="风险等级")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="上下文信息")


class MethodResult(BaseModel):
    """方法执行结果"""
    method_name: str = Field(..., description="方法名称")
    content: str = Field(..., description="方法内容/话术")
    suggestions: Optional[List[str]] = Field(default_factory=list, description="建议列表")


class StrategyResponse(BaseModel):
    """策略响应"""
    strategy: str = Field(..., description="策略名称")
    methods: List[MethodResult] = Field(default_factory=list, description="执行的方法列表")
    response_text: str = Field(..., description="最终回复文本")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")


class StateJudgment(BaseModel):
    """状态判断结果"""
    stage: StageType = Field(..., description="状态类型")
    intensity: IntensityType = Field(..., description="强度")
    risk: RiskType = Field(..., description="风险等级")


class MusicSuggestion(BaseModel):
    """音乐推荐"""
    song_name: str = Field(..., description="歌曲名称")
    artist: str = Field(..., description="演唱者")
    description: str = Field(..., description="歌曲描述")
    emotion: str = Field(..., description="适用情绪")


class BreathingExercise(BaseModel):
    """呼吸练习"""
    name: str = Field(..., description="练习名称")
    steps: List[str] = Field(..., description="步骤说明")
    duration_seconds: int = Field(..., description="预计时长（秒）")
    suitable_for: str = Field(..., description="适用场景")


class InterestActivity(BaseModel):
    """兴趣活动建议"""
    name: str = Field(..., description="活动名称")
    description: str = Field(..., description="活动描述")
    suitable_for: List[str] = Field(default_factory=list, description="适用情绪")


class HealthTip(BaseModel):
    """健康小贴士"""
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    category: str = Field(..., description="分类")


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="角色：user/assistant")
    content: str = Field(..., description="消息内容")
    timestamp: str = Field(..., description="时间戳")
    emotion: Optional[str] = Field(None, description="情绪类型")
    strategy: Optional[str] = Field(None, description="使用的策略")


class ConversationHistory(BaseModel):
    """对话历史"""
    session_id: str = Field(..., description="会话 ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="消息列表")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    max_messages: int = Field(default=20, description="最大保留消息数")
    
    def add_message(self, role: str, content: str, emotion: str = None, strategy: str = None):
        """添加消息"""
        from datetime import datetime
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            emotion=emotion,
            strategy=strategy
        )
        self.messages.append(message)
        
        # 限制消息数量
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        self.updated_at = datetime.now().isoformat()
    
    def get_recent_messages(self, limit: int = 5) -> List[ChatMessage]:
        """获取最近的消息"""
        return self.messages[-limit:] if self.messages else []
    
    def to_llm_format(self, limit: int = 10) -> str:
        """转换为 LLM 可读的上下文格式"""
        recent = self.get_recent_messages(limit)
        if not recent:
            return ""
        
        context_lines = []
        for msg in recent:
            role_cn = "用户" if msg.role == "user" else "助手"
            context_lines.append(f"{role_cn}: {msg.content}")
        
        return "\n".join(context_lines)