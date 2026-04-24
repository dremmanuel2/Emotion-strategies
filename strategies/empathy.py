"""
共情策略 - 理解和接纳用户情绪
"""
from typing import List
from loguru import logger

from models import UserInput, StrategyResponse, MethodResult, StateJudgment, EmotionType
from strategies.base import BaseStrategy


class EmpathyStrategy(BaseStrategy):
    """共情策略"""
    
    def __init__(self):
        super().__init__()
        self.name = "EMPATHY"
        self.description = "【共情陪伴】理解和接纳用户的消极情绪，通过情绪认可、经历验证和陪伴表达来建立情感连接"
        self.suitable_emotions = ["sad", "anxious", "angry"]
        self.suitable_stages = ["venting", "neutral"]
        self.suitable_intensities = ["low", "medium", "high"]
        self.suitable_risks = ["low"]
        self.methods_info = [
            {"name": "情绪共情", "desc": "根据具体情绪类型（悲伤/焦虑/愤怒）提供针对性的理解和认可"},
            {"name": "经历认可", "desc": "认可用户感受的真实性和重要性，消除自责"},
            {"name": "陪伴表达", "desc": "表达陪伴意愿，让用户知道有人愿意倾听"}
        ]
        
        # 不同情绪的共情重点
        self.empathy_focus = {
            EmotionType.SAD: {
                "focus": "承认丧失的痛苦",
                "template": "失去{loss}，这种痛苦是难以言喻的。难过是正常的，不要强忍着。"
            },
            EmotionType.ANXIOUS: {
                "focus": "理解担忧的感受",
                "template": "能感觉到你现在很担心。这种事情确实让人心里不踏实。"
            },
            EmotionType.ANGRY: {
                "focus": "认可情绪的合理性",
                "template": "遇到这种事，生气是很正常的。换做是我，可能也会不高兴。"
            },
            EmotionType.NEUTRAL: {
                "focus": "表达陪伴意愿",
                "template": "我在这儿陪着你，你想聊什么都可以。"
            }
        }
    
    def can_handle(self, user_input: UserInput, state: StateJudgment) -> bool:
        """所有消极情绪都可以使用共情"""
        return user_input.emotion in [EmotionType.SAD, EmotionType.ANXIOUS, EmotionType.ANGRY]
    
    async def execute(self, user_input: UserInput, state: StateJudgment) -> StrategyResponse:
        """执行共情策略"""
        logger.info(f"[{self.name}] 执行共情策略，情绪类型：{user_input.emotion}")
        
        methods: List[MethodResult] = []
        
        # 情绪共情
        empathy_method = self._emotion_empathy(user_input)
        methods.append(empathy_method)
        
        # 经历认可
        validation_method = self._validate_experience(user_input)
        methods.append(validation_method)
        
        # 陪伴表达
        company_method = self._express_company()
        methods.append(company_method)
        
        # 生成回复
        response_text = self._generate_response(methods)
        
        return StrategyResponse(
            strategy=self.name,
            methods=methods,
            response_text=response_text,
            metadata={
                "emotion": user_input.emotion.value,
                "empathy_type": "emotional_validation"
            }
        )
    
    def _emotion_empathy(self, user_input: UserInput) -> MethodResult:
        """情绪共情"""
        emotion = user_input.emotion
        
        if emotion == EmotionType.SAD:
            content = (
                "听起来你真的有点疲惫和失落。\n"
                "好像是付出了很多，但结果却没有回应。\n"
                "这种落差其实挺打击人的，换做是谁都会不好受。"
            )
        elif emotion == EmotionType.ANXIOUS:
            content = (
                "能感觉到你现在很担心，也有些不安。\n"
                "面对不确定的事情，这种担心是很正常的。\n"
                "你愿意多说是因为什么担心吗？"
            )
        elif emotion == EmotionType.ANGRY:
            content = (
                "遇到这种事，生气是很正常的。\n"
                "换做是我，可能也会不高兴。\n"
                "你心里一定很不好受。"
            )
        else:
            content = "我能理解你现在的感受。"
        
        self._log_execution("情绪共情", f"情绪：{emotion.value}")
        return self._create_method_result("情绪共情", content)
    
    def _validate_experience(self, user_input: UserInput) -> MethodResult:
        """经历认可"""
        content = (
            "你的感受是真实的，也是重要的。\n"
            "每个人都有情绪低落的时候，这不代表你脆弱。\n"
            "你已经很努力了，这不容易。"
        )
        self._log_execution("经历认可")
        return self._create_method_result("经历认可", content)
    
    def _express_company(self) -> MethodResult:
        """陪伴表达"""
        content = (
            "我在这儿陪着你。\n"
            "有什么想说的都可以跟我说，我愿意听。"
        )
        self._log_execution("陪伴表达")
        return self._create_method_result("陪伴表达", content)
    
    def _generate_response(self, methods: List[MethodResult]) -> str:
        """生成回复"""
        parts = [m.content for m in methods]
        return "\n\n".join(parts)