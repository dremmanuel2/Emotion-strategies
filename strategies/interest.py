"""
兴趣转移策略 - 转移注意力到积极事物
"""
from typing import List, Dict
from loguru import logger
import asyncio

from models import UserInput, StrategyResponse, MethodResult, StateJudgment, EmotionType
from strategies.base import BaseStrategy


class InterestRedirectStrategy(BaseStrategy):
    """兴趣转移策略"""
    
    def __init__(self):
        super().__init__()
        self.name = "INTEREST_REDIRECT"
        self.description = "【兴趣转移】将注意力从消极情绪转移到积极活动，包括微小成就清单、日常掌控清单、兴趣话题探索等"
        self.suitable_emotions = ["sad", "anxious", "angry", "neutral"]
        self.suitable_stages = ["help", "neutral"]
        self.suitable_intensities = ["low", "medium"]
        self.suitable_risks = ["low"]
        self.methods_info = [
            {"name": "微小成就清单", "desc": "列出简单易完成的小目标（叠被子、散步、喝水），适用于悲伤情绪"},
            {"name": "日常掌控清单", "desc": "建立规律的日常活动（固定起床、散步、看新闻），适用于焦虑情绪"},
            {"name": "兴趣话题探索", "desc": "探索老年人的兴趣爱好（养花、书法、太极、戏曲等），适用于愤怒或日常状态"},
            {"name": "日常陪伴", "desc": "日常问候和关心（询问吃饭、天气、身体状况）"},
            {"name": "阳光暴露法", "desc": "建议上午晒太阳 20 分钟，改善心情和身体健康"},
            {"name": "回忆锚定法", "desc": "通过老照片回忆美好时光，建立积极情绪锚点"}
        ]
        
        # 方法选择映射
        self.method_mapping = {
            EmotionType.SAD: self._small_achievement_method,
            EmotionType.ANXIOUS: self._daily_control_method,
            EmotionType.ANGRY: self._hobby_exploration_method,
        }
        
        # 老年人兴趣话题
        self.elderly_interests = [
            "养生保健",
            "养花/园艺",
            "书法绘画",
            "太极/广场舞",
            "戏曲/老歌",
            "孙辈/家庭",
            "旅游/散步",
            "烹饪/美食"
        ]
    
    def can_handle(self, user_input: UserInput, state: StateJudgment) -> bool:
        """求助中低密度或日常状态使用此策略"""
        return (
            (state.stage.value == "help" and state.intensity in ["low", "medium"]) or
            (state.stage.value == "neutral" and user_input.emotion == EmotionType.NEUTRAL)
        )
    
    async def execute(self, user_input: UserInput, state: StateJudgment) -> StrategyResponse:
        """执行兴趣转移策略"""
        logger.info(f"[{self.name}] 执行兴趣转移策略，情绪：{user_input.emotion}")
        
        methods: List[MethodResult] = []
        
        # 根据情绪选择方法
        emotion = user_input.emotion
        if emotion in self.method_mapping:
            method_func = self.method_mapping[emotion]
        else:
            method_func = self._hobby_exploration_method
        
        methods.append(await method_func(user_input))
        
        # 如果是日常状态，加上日常陪伴
        if state.stage.value == "neutral":
            methods.append(self._daily_company_method())
        
        # 生成回复
        response_text = self._generate_response(methods)
        
        return StrategyResponse(
            strategy=self.name,
            methods=methods,
            response_text=response_text,
            metadata={
                "emotion": emotion.value,
                "stage": state.stage.value
            }
        )
    
    async def _small_achievement_method(self, user_input: UserInput) -> MethodResult:
        """微小成就清单 - 悲伤情绪"""
        content = (
            "咱们每天给自己定 3 个小目标，很简单的那种。\n"
            "比如：\n"
            "• 早上起床叠好被子\n"
            "• 下楼走 5 分钟\n"
            "• 喝一杯温水\n"
            "每完成一个，就打个勾。\n"
            "别小看这些事，做完心里会很有成就感。"
        )
        suggestions = [
            "起床叠被子",
            "下楼走 5 分钟",
            "喝一杯温水",
            "听一首老歌",
            "浇浇花"
        ]
        self._log_execution("微小成就清单")
        return self._create_method_result("微小成就清单", content, suggestions)
    
    async def _daily_control_method(self, user_input: UserInput) -> MethodResult:
        """日常掌控清单 - 焦虑情绪"""
        content = (
            "咱们每天固定做几件小事，让生活有规律。\n"
            "比如：\n"
            "• 早上起床先喝一杯温水\n"
            "• 下午去公园走一圈\n"
            "• 晚上准时看新闻联播\n"
            "这样每天都有点期待，心里也踏实。"
        )
        suggestions = [
            "固定时间起床",
            "固定时间散步",
            "固定时间看新闻",
            "固定时间吃饭",
            "固定时间休息"
        ]
        self._log_execution("日常掌控清单")
        return self._create_method_result("日常掌控清单", content, suggestions)
    
    async def _hobby_exploration_method(self, user_input: UserInput) -> MethodResult:
        """兴趣话题探索"""
        content = (
            "对了，你平时喜欢做些什么呀？\n"
            "养养花、听听戏，或者跟老朋友聊聊天。\n"
            "做点自己喜欢的事情，心情会好很多。\n"
            f"你最近有没有发现什么好玩的事儿？\n"
            f"我听说很多叔叔阿姨喜欢{self._get_random_interest()}，你有试过吗？"
        )
        self._log_execution("兴趣话题探索")
        return self._create_method_result("兴趣话题探索", content)
    
    def _daily_company_method(self) -> MethodResult:
        """日常陪伴方法"""
        content = (
            "今天过得怎么样呀？\n"
            "吃饭了吗？最近天气变化大，要注意身体。\n"
            "有什么想聊的都可以跟我说，我在这儿陪着你。"
        )
        self._log_execution("日常陪伴")
        return self._create_method_result("日常陪伴", content)
    
    async def _sun_exposure_method(self, user_input: UserInput) -> MethodResult:
        """阳光暴露法"""
        content = (
            "今天上午阳光好的时候，出去晒晒太阳吧。\n"
            "就在楼下站一会儿，或者慢慢走一圈。\n"
            "不用戴帽子，让阳光照在脸上。\n"
            "晒 20 分钟就行，对身体和心情都有好处。"
        )
        suggestions = [
            "上午 9-10 点最佳",
            "注意保暖",
            "可以顺便散散步"
        ]
        self._log_execution("阳光暴露法")
        return self._create_method_result("阳光暴露法", content, suggestions)
    
    async def _memory_anchor_method(self, user_input: UserInput) -> MethodResult:
        """回忆锚定法"""
        content = (
            "要不要看看以前的老照片？\n"
            "挑一张你特别开心的照片。\n"
            "跟我讲讲这张照片是什么时候拍的？\n"
            "当时发生了什么有趣的事？\n"
            "回想那些美好的时光，心里是不是暖暖的？"
        )
        self._log_execution("回忆锚定法")
        return self._create_method_result("回忆锚定法", content)
    
    def _get_random_interest(self) -> str:
        """获取随机兴趣话题"""
        import random
        return random.choice(self.elderly_interests)
    
    def _generate_response(self, methods: List[MethodResult]) -> str:
        """生成回复"""
        parts = [m.content for m in methods]
        return "\n\n".join(parts)