"""
日常陪伴策略 - 中性情绪日常聊天
"""
from typing import List, Dict
from loguru import logger
import asyncio

from models import UserInput, StrategyResponse, MethodResult, StateJudgment, EmotionType
from strategies.base import BaseStrategy


class CompanyStrategy(BaseStrategy):
    """日常陪伴策略"""
    
    def __init__(self):
        super().__init__()
        self.name = "COMPANY"
        self.description = "【日常陪伴】针对中性情绪的日常聊天，根据上下文（疲劳/无聊/想聊天/独居/睡眠问题）提供针对性陪伴"
        self.suitable_emotions = ["neutral"]
        self.suitable_stages = ["neutral"]
        self.suitable_intensities = ["low", "medium"]
        self.suitable_risks = ["low"]
        self.methods_info = [
            {"name": "日常问候", "desc": "询问当天情况、吃饭情况、天气变化等日常关心"},
            {"name": "微休息练习", "desc": "针对疲劳状态，引导舒适姿势和深呼吸放松"},
            {"name": "兴趣话题探索", "desc": "针对无聊状态，推荐养花、听戏、写字、散步等活动"},
            {"name": "倾听陪伴", "desc": "针对想聊天状态，表达愿意倾听家常里短或心里话"},
            {"name": "情绪急救包建议", "desc": "针对独居状态，建议准备装有照片、信件、歌单等的情绪急救盒"},
            {"name": "睡眠卫生建议", "desc": "针对睡眠问题，提供固定作息、睡前放松等建议"},
            {"name": "身体照顾建议", "desc": "日常身体健康提醒（多喝水、出去走走、早点休息）"}
        ]
        
        # 方法映射
        self.context_methods = {
            "tired": self._micro_rest_method,
            "bored": self._hobby_exploration_method,
            "want_chat": self._listening_method,
            "living_alone": self._emotion_kit_method,
            "sleep_problem": self._sleep_hygiene_method,
            "default": self._daily_greeting_method
        }
    
    def can_handle(self, user_input: UserInput, state: StateJudgment) -> bool:
        """中性情绪日常状态使用此策略"""
        return (
            user_input.emotion == EmotionType.NEUTRAL and
            state.stage.value == "neutral"
        )
    
    async def execute(self, user_input: UserInput, state: StateJudgment) -> StrategyResponse:
        """执行日常陪伴策略"""
        logger.info(f"[{self.name}] 执行日常陪伴策略")
        
        methods: List[MethodResult] = []
        
        # 获取上下文
        context = user_input.context or {}
        
        # 根据上下文选择方法
        selected_context = "default"
        for key in self.context_methods.keys():
            if context.get(key):
                selected_context = key
                break
        
        method_func = self.context_methods.get(selected_context, self._daily_greeting_method)
        methods.append(await method_func(user_input))
        
        # 生成回复
        response_text = self._generate_response(methods)
        
        return StrategyResponse(
            strategy=self.name,
            methods=methods,
            response_text=response_text,
            metadata={
                "context": selected_context,
                "emotion": "neutral"
            }
        )
    
    async def _daily_greeting_method(self, user_input: UserInput) -> MethodResult:
        """日常问候"""
        content = (
            "今天过得怎么样呀？\n"
            "吃饭了吗？最近天气变化大，要注意身体。\n"
            "有什么想聊的都可以跟我说，我在这儿陪着你。"
        )
        self._log_execution("日常问候")
        return self._create_method_result("日常问候", content)
    
    async def _micro_rest_method(self, user_input: UserInput) -> MethodResult:
        """微休息练习"""
        content = (
            "累了的话，可以歇一会儿。\n"
            "找个舒服的姿势，做 3 次深呼吸。\n"
            "每次吸气的时候，感觉肩膀放松。\n"
            "呼气的时候，嘴角微微上扬。\n"
            "1 分钟就行，做完会轻松很多。"
        )
        self._log_execution("微休息练习")
        return self._create_method_result("微休息练习", content)
    
    async def _hobby_exploration_method(self, user_input: UserInput) -> MethodResult:
        """兴趣话题探索"""
        content = (
            "无聊的话，可以找点喜欢的事情做做。\n"
            "比如：\n"
            "• 养养花，看着它们长大很有成就感\n"
            "• 听听戏，经典老歌永远好听\n"
            "• 写写字，书法能让人静心\n"
            "• 出去走走，晒晒太阳对身体好\n"
            "你平时喜欢做什么呀？"
        )
        self._log_execution("兴趣话题探索")
        return self._create_method_result("兴趣话题探索", content)
    
    async def _listening_method(self, user_input: UserInput) -> MethodResult:
        """倾听陪伴"""
        content = (
            "好啊，你说，我听着呢。\n"
            "想聊什么都可以，家常里短也好，心里话也好。\n"
            "我在这儿陪着你。"
        )
        self._log_execution("倾听陪伴")
        return self._create_method_result("倾听陪伴", content)
    
    async def _emotion_kit_method(self, user_input: UserInput) -> MethodResult:
        """情绪急救包建议"""
        content = (
            "可以准备一个小盒子，放点能让你开心的东西。\n"
            "比如：\n"
            "• 家人的照片\n"
            "• 老朋友的信\n"
            "• 喜欢的歌单\n"
            "• 其他有意义的东西\n"
            "心情不好的时候，就打开看看。\n"
            "你有什么特别珍藏的东西吗？"
        )
        self._log_execution("情绪急救包建议")
        return self._create_method_result("情绪急救包建议", content)
    
    async def _sleep_hygiene_method(self, user_input: UserInput) -> MethodResult:
        """睡眠卫生建议"""
        content = (
            "晚上睡不好的话，可以试试：\n"
            "• 固定时间睡觉起床，周末也别差太多\n"
            "• 睡前 1 小时别看手机\n"
            "• 卧室光线暗一点，安静一点\n"
            "• 要是 30 分钟还睡不着，就起来坐会儿\n"
            "你平时几点睡觉呀？"
        )
        self._log_execution("睡眠卫生建议")
        return self._create_method_result("睡眠卫生建议", content)
    
    async def _body_care_method(self, user_input: UserInput) -> MethodResult:
        """身体照顾建议"""
        content = (
            "咱们每天照顾好身体，心情也会好。\n"
            "今天记得：\n"
            "• 多喝水\n"
            "• 出去走走\n"
            "• 早点休息\n"
            "身体好了，心里才舒坦。\n"
            "你今天喝水了吗？"
        )
        self._log_execution("身体照顾建议")
        return self._create_method_result("身体照顾建议", content)
    
    def _generate_response(self, methods: List[MethodResult]) -> str:
        """生成回复"""
        parts = [m.content for m in methods]
        return "\n\n".join(parts)