"""
呼吸引导策略 - 各种呼吸练习方法
"""
from typing import List, Dict
from loguru import logger

from models import UserInput, StrategyResponse, MethodResult, StateJudgment, EmotionType, IntensityType
from strategies.base import BaseStrategy


class BreathingStrategy(BaseStrategy):
    """呼吸引导策略"""
    
    def __init__(self):
        super().__init__()
        self.name = "BREATHING"
        self.description = "【呼吸练习】针对高焦虑或高密度求助状态，提供结构化的呼吸练习指导（4-7-8/5-5-5/方块/身体扫描）"
        self.suitable_emotions = ["anxious", "sad"]
        self.suitable_stages = ["venting", "help"]
        self.suitable_intensities = ["medium", "high"]
        self.suitable_risks = ["low"]
        self.methods_info = [
            {"name": "引导开始", "desc": "邀请用户跟随节奏进行呼吸练习"},
            {"name": "4-7-8 呼吸法", "desc": "吸气 4 秒 - 屏息 7 秒 - 呼气 8 秒，适用于急性焦虑发作"},
            {"name": "5-5-5 呼吸法", "desc": "吸气 - 屏息 - 呼气各 5 秒，简化版适合老年人日常使用"},
            {"name": "方块呼吸法", "desc": "配合视觉焦点的 4-4-4-4 呼吸，适用于悲伤情绪"},
            {"name": "身体扫描呼吸法", "desc": "配合身体感知的呼吸练习，适用于睡前放松"},
            {"name": "结束安抚", "desc": "肯定用户的练习效果，鼓励后续使用"}
        ]
        
        # 呼吸方法库
        self.breathing_methods = {
            "4-7-8": self._breathing_478,
            "5-5-5": self._breathing_555,
            "square": self._breathing_square,
            "body_scan": self._breathing_body_scan
        }
    
    def can_handle(self, user_input: UserInput, state: StateJudgment) -> bool:
        """高密度焦虑或求助状态使用此策略"""
        return (
            (user_input.emotion == EmotionType.ANXIOUS and 
             state.intensity in [IntensityType.MEDIUM, IntensityType.HIGH]) or
            (state.stage.value == "help" and state.intensity == IntensityType.HIGH)
        )
    
    async def execute(self, user_input: UserInput, state: StateJudgment) -> StrategyResponse:
        """执行呼吸引导策略"""
        logger.info(f"[{self.name}] 执行呼吸引导策略")
        
        methods: List[MethodResult] = []
        
        # 根据状态选择呼吸方法
        breathing_type = self._select_breathing_type(user_input, state)
        breathing_method = self.breathing_methods.get(breathing_type, self._breathing_555)
        
        # 引导开始
        intro_method = self._breathing_intro()
        methods.append(intro_method)
        
        # 呼吸练习
        methods.append(await breathing_method())
        
        # 结束安抚
        outro_method = self._breathing_outro()
        methods.append(outro_method)
        
        # 生成回复
        response_text = self._generate_response(methods)
        
        return StrategyResponse(
            strategy=self.name,
            methods=methods,
            response_text=response_text,
            metadata={
                "breathing_type": breathing_type,
                "emotion": user_input.emotion.value
            }
        )
    
    def _select_breathing_type(self, user_input: UserInput, state: StateJudgment) -> str:
        """根据状态选择呼吸方法"""
        if user_input.emotion == EmotionType.ANXIOUS and state.intensity == IntensityType.HIGH:
            return "4-7-8"  # 急性焦虑用 4-7-8
        elif user_input.emotion == EmotionType.SAD:
            return "square"  # 悲伤用方块呼吸
        elif state.stage.value == "help" and state.intensity == IntensityType.HIGH:
            return "5-5-5"  # 高密度求助用简化版
        else:
            return "5-5-5"  # 默认简化版
    
    def _breathing_intro(self) -> MethodResult:
        """引导开始"""
        content = (
            "来，现在跟我一起做几个深呼吸。\n"
            "不用想那么多，跟着我的节奏来就好。"
        )
        self._log_execution("引导开始")
        return self._create_method_result("引导开始", content)
    
    async def _breathing_478(self) -> MethodResult:
        """4-7-8 呼吸法 - 急性焦虑"""
        content = (
            "用鼻子慢慢吸气，数 4 下……1、2、3、4\n"
            "好，屏住呼吸，数 7 下……1、2、3、4、5、6、7\n"
            "现在用嘴巴慢慢呼气，数 8 下……1、2、3、4、5、6、7、8\n"
            "对，就是这样，再来一次。\n"
            "重复 5-10 次，每次结束后停顿 10 秒。"
        )
        suggestions = [
            "适合睡前使用",
            "适合急性焦虑发作时",
            "重复 5-10 次"
        ]
        self._log_execution("4-7-8 呼吸法")
        return self._create_method_result("4-7-8 呼吸法", content, suggestions)
    
    async def _breathing_555(self) -> MethodResult:
        """5-5-5 呼吸法 - 简化版"""
        content = (
            "咱们做个简单的呼吸练习。\n"
            "吸气……5 下……1、2、3、4、5\n"
            "屏住……5 下……1、2、3、4、5\n"
            "呼气……5 下……1、2、3、4、5\n"
            "很好，再来两次。"
        )
        suggestions = [
            "数字简单，容易记忆",
            "适合老年人",
            "任何焦虑场景都可以用"
        ]
        self._log_execution("5-5-5 呼吸法")
        return self._create_method_result("5-5-5 呼吸法", content, suggestions)
    
    async def _breathing_square(self) -> MethodResult:
        """方块呼吸法 - 配合视觉"""
        content = (
            "找个方形的东西看着，比如手机或者桌子。\n"
            "吸气 4 秒……看着这个方形……1、2、3、4\n"
            "屏住 4 秒……继续看着……1、2、3、4\n"
            "呼气 4 秒……还是看着它……1、2、3、4\n"
            "屏住 4 秒……1、2、3、4\n"
            "再来几次，注意力集中在呼吸上。"
        )
        suggestions = [
            "配合视觉焦点",
            "分散注意力",
            "适合悲伤情绪"
        ]
        self._log_execution("方块呼吸法")
        return self._create_method_result("方块呼吸法", content, suggestions)
    
    async def _breathing_body_scan(self) -> MethodResult:
        """身体扫描呼吸法 - 睡前"""
        content = (
            "躺好，闭上眼睛。\n"
            "慢慢吸气……感受空气进入肚子……肚子鼓起来\n"
            "慢慢呼气……感受肚子瘪下去……\n"
            "同时，从脚开始，感受每个部位……\n"
            "脚趾……脚掌……小腿……大腿……\n"
            "一直到头，感受每个地方慢慢放松。\n"
            "要是走神了，就把注意力拉回呼吸。"
        )
        suggestions = [
            "适合睡前使用",
            "帮助放松身体",
            "改善睡眠质量"
        ]
        self._log_execution("身体扫描呼吸法")
        return self._create_method_result("身体扫描呼吸法", content, suggestions)
    
    def _breathing_outro(self) -> MethodResult:
        """结束安抚"""
        content = (
            "做完深呼吸，有没有感觉稍微放松一点？\n"
            "要是还想做，可以随时再来几次。\n"
            "记住这个感觉，需要的时候就用这个方法。"
        )
        self._log_execution("结束安抚")
        return self._create_method_result("结束安抚", content)
    
    def _generate_response(self, methods: List[MethodResult]) -> str:
        """生成回复"""
        parts = [m.content for m in methods]
        return "\n\n".join(parts)