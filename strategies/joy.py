"""
喜悦分享策略 - 积极情绪处理
"""
from typing import List
from loguru import logger

from models import UserInput, StrategyResponse, MethodResult, StateJudgment, EmotionType, IntensityType
from strategies.base import BaseStrategy


class JoyShareStrategy(BaseStrategy):
    """喜悦分享策略"""
    
    def __init__(self):
        super().__init__()
        self.name = "JOY_SHARE"
        self.description = "【喜悦分享】针对积极情绪状态，通过分享喜悦、鼓励助兴、记录美好等方式强化和延续积极情绪"
        self.suitable_emotions = ["positive"]
        self.suitable_stages = ["venting", "help", "neutral"]
        self.suitable_intensities = ["low", "medium", "high"]
        self.suitable_risks = ["low"]
        self.methods_info = [
            {"name": "分享喜悦", "desc": "表达为用户高兴的心情，邀请用户分享开心事"},
            {"name": "鼓励听音乐", "desc": "高强度积极情绪时推荐欢快老歌助兴（南泥湾、洪湖水等）"},
            {"name": "鼓励记录", "desc": "中强度积极情绪时鼓励记录美好时刻以便日后回味"},
            {"name": "微休息建议", "desc": "低强度积极情绪时建议适度休息和深呼吸"},
            {"name": "询问近况", "desc": "询问当天整体情况，鼓励分享更多开心事"}
        ]
    
    def can_handle(self, user_input: UserInput, state: StateJudgment) -> bool:
        """积极情绪使用此策略"""
        return user_input.emotion == EmotionType.POSITIVE
    
    async def execute(self, user_input: UserInput, state: StateJudgment) -> StrategyResponse:
        """执行喜悦分享策略"""
        logger.info(f"[{self.name}] 执行喜悦分享策略，强度：{state.intensity.value}")
        
        methods: List[MethodResult] = []
        
        # 分享喜悦
        share_method = self._share_joy()
        methods.append(share_method)
        
        # 根据强度选择方法
        if state.intensity == IntensityType.HIGH:
            methods.append(self._encourage_music())
        elif state.intensity == IntensityType.MEDIUM:
            methods.append(self._encourage_recording())
        else:
            methods.append(self._micro_rest_suggestion())
        
        # 询问近况
        methods.append(self._ask_about_day())
        
        # 生成回复
        response_text = self._generate_response(methods)
        
        return StrategyResponse(
            strategy=self.name,
            methods=methods,
            response_text=response_text,
            metadata={
                "emotion": "positive",
                "intensity": state.intensity.value
            }
        )
    
    def _share_joy(self) -> MethodResult:
        """分享喜悦"""
        content = (
            "太好了！听到你心情这么好，我也很开心！\n"
            "这种感觉真好，要好好享受。\n"
            "今天有什么特别的事情让你这么高兴吗？"
        )
        self._log_execution("分享喜悦")
        return self._create_method_result("分享喜悦", content)
    
    def _encourage_music(self) -> MethodResult:
        """鼓励听音乐助兴"""
        content = (
            "心情这么好，要不要放点你喜欢的歌助助兴？\n"
            "我这儿有几首欢快的老歌：\n"
            "• 《南泥湾》- 郭兰英\n"
            "• 《洪湖水浪打浪》\n"
            "• 《我的祖国》\n"
            "你想听哪首？或者你有其他喜欢的也可以告诉我。"
        )
        self._log_execution("鼓励听音乐")
        return self._create_method_result("鼓励听音乐", content)
    
    def _encourage_recording(self) -> MethodResult:
        """鼓励记录美好时刻"""
        content = (
            "今天这么开心，可以记下来。\n"
            "以后翻看的时候，还能想起现在的好心情。\n"
            "你说是吧？"
        )
        self._log_execution("鼓励记录")
        return self._create_method_result("鼓励记录", content)
    
    def _micro_rest_suggestion(self) -> MethodResult:
        """微休息建议"""
        content = (
            "心情好也要注意休息哦。\n"
            "找个舒服的姿势，做 3 次深呼吸。\n"
            "每次吸气的时候，感觉肩膀放松。\n"
            "呼气的时候，嘴角微微上扬。"
        )
        self._log_execution("微休息建议")
        return self._create_method_result("微休息建议", content)
    
    def _ask_about_day(self) -> MethodResult:
        """询问近况"""
        content = (
            "今天过得怎么样呀？\n"
            "有没有其他开心的事想跟我分享？"
        )
        self._log_execution("询问近况")
        return self._create_method_result("询问近况", content)
    
    def _generate_response(self, methods: List[MethodResult]) -> str:
        """生成回复"""
        parts = [m.content for m in methods]
        return "\n\n".join(parts)