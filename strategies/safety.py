"""
安全干预策略 - 高风险情况
"""
from typing import List, Optional
from loguru import logger

from models import UserInput, StrategyResponse, MethodResult, StateJudgment, RiskType
from strategies.base import BaseStrategy
from config import get_settings


class SafetyStrategy(BaseStrategy):
    """安全干预策略"""
    
    def __init__(self):
        super().__init__()
        self.name = "SAFETY"
        self.description = "【安全干预】高风险情况下的紧急心理支持策略，提供关心表达、专业资源推荐和危机干预"
        self.suitable_emotions = ["sad", "angry", "anxious", "neutral"]
        self.suitable_stages = ["venting", "help", "neutral"]
        self.suitable_intensities = ["high"]
        self.suitable_risks = ["high"]
        self.methods_info = [
            {"name": "表达关心", "desc": "表达对用户安全的担忧和关心，认可其感受的重要性"},
            {"name": "建议寻求现实帮助", "desc": "鼓励用户联系信任的人或专业心理咨询师"},
            {"name": "提供心理援助热线", "desc": "提供全国和地区心理援助热线联系方式"}
        ]
        self.settings = get_settings()
    
    def can_handle(self, user_input: UserInput, state: StateJudgment) -> bool:
        """高风险情况使用此策略"""
        return state.risk == RiskType.HIGH
    
    async def execute(self, user_input: UserInput, state: StateJudgment) -> StrategyResponse:
        """执行安全干预"""
        logger.warning(f"[{self.name}] 检测到高风险情况，启动安全干预")
        
        methods: List[MethodResult] = []
        
        # 表达关心
        care_method = self._express_care(user_input.text)
        methods.append(care_method)
        
        # 建议寻求现实帮助
        help_method = self._suggest_real_help()
        methods.append(help_method)
        
        # 提供心理援助热线
        hotline_method = self._provide_hotlines()
        methods.append(hotline_method)
        
        # 生成回复文本
        response_text = self._generate_response(care_method, help_method, hotline_method)
        
        return StrategyResponse(
            strategy=self.name,
            methods=methods,
            response_text=response_text,
            metadata={
                "risk_level": "high",
                "requires_followup": True
            }
        )
    
    def _express_care(self, user_text: str) -> MethodResult:
        """表达关心和担忧"""
        content = (
            "听到你这样说，我真的很担心你现在的状态。\n"
            "这种感觉一定非常难受，让你有了这样的想法。\n"
            "你不需要一个人扛着这些，你的感受是重要的。"
        )
        self._log_execution("表达关心")
        return self._create_method_result("表达关心", content)
    
    def _suggest_real_help(self) -> MethodResult:
        """建议寻求现实帮助"""
        content = (
            "你不需要一个人面对这些困难。\n"
            "可以考虑找一个信任的人聊聊，比如家人、朋友，或者专业的心理咨询师。\n"
            "寻求帮助是勇敢的表现，不是软弱。"
        )
        suggestions = [
            "联系一个信任的家人或朋友",
            "预约心理咨询师",
            "如有紧急情况，立即就医"
        ]
        self._log_execution("建议寻求现实帮助")
        return self._create_method_result("建议寻求现实帮助", content, suggestions)
    
    def _provide_hotlines(self) -> MethodResult:
        """提供心理援助热线"""
        content = (
            "如果你需要即时支持，可以联系以下心理援助热线：\n"
            f"• 全国希望 24 热线：{self.settings.HOTLINE_HOPE}（24 小时）\n"
            f"• 全国心理援助热线：{self.settings.HOTLINE_NATIONAL}（24 小时）\n"
            f"• 北京市心理援助热线：{self.settings.HOTLINE_BEIJING}\n"
            "这些热线都有专业人员接听，他们会耐心听你说。"
        )
        self._log_execution("提供心理援助热线")
        return self._create_method_result("提供心理援助热线", content)
    
    def _generate_response(self, care: MethodResult, help_sug: MethodResult, hotline: MethodResult) -> str:
        """生成完整回复"""
        return (
            f"{care.content}\n\n"
            f"{help_sug.content}\n\n"
            f"{hotline.content}\n\n"
            "如果你愿意，也可以和我多说一点，我在这里听你。"
        )