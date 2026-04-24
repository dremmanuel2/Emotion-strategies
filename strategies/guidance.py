"""
轻建议策略 - 给用户温和建议
"""
from typing import List, Dict
from loguru import logger

from models import UserInput, StrategyResponse, MethodResult, StateJudgment, StageType, IntensityType
from strategies.base import BaseStrategy


class GuidanceLightStrategy(BaseStrategy):
    """轻建议策略"""
    
    def __init__(self):
        super().__init__()
        self.name = "GUIDANCE_LIGHT"
        self.description = "【温和建议】针对求助状态的用户，先共情再根据问题类型（决策/情绪/动机/睡眠/健康）提供温和、可操作的建议"
        self.suitable_emotions = ["sad", "anxious", "angry", "neutral"]
        self.suitable_stages = ["help"]
        self.suitable_intensities = ["low", "medium", "high"]
        self.suitable_risks = ["low"]
        self.methods_info = [
            {"name": "初始共情", "desc": "在提供建议前先表达理解和共情"},
            {"name": "认知重构三问", "desc": "引导用户反思证据、最坏结果和可行行动（适用于决策问题）"},
            {"name": "呼吸法建议", "desc": "建议通过深呼吸平复情绪后再解决问题（适用于情绪问题）"},
            {"name": "微小成就清单", "desc": "提供简单易行的小目标建议（适用于动机问题）"},
            {"name": "睡眠建议", "desc": "提供睡眠卫生习惯建议（适用于睡眠问题）"},
            {"name": "阳光暴露法", "desc": "建议户外晒太阳改善心情（适用于健康担忧）"}
        ]
        
        # 问题类型对应的方法
        self.problem_methods = {
            "decision": self._cognitive_restructuring,
            "emotional": self._breathing_suggestion,
            "motivation": self._small_achievement,
            "sleep": self._sleep_advice,
            "health_worry": self._sun_exposure,
            "default": self._general_advice
        }
    
    def can_handle(self, user_input: UserInput, state: StateJudgment) -> bool:
        """求助状态使用此策略"""
        return state.stage == StageType.HELP
    
    async def execute(self, user_input: UserInput, state: StateJudgment) -> StrategyResponse:
        """执行轻建议策略"""
        logger.info(f"[{self.name}] 执行轻建议策略，强度：{state.intensity.value}")
        
        methods: List[MethodResult] = []
        
        # 先共情
        empathy_method = self._initial_empathy()
        methods.append(empathy_method)
        
        # 根据问题类型给建议
        problem_type = user_input.context.get("problem_type", "default")
        advice_method = await self._get_advice_method(problem_type)
        methods.append(advice_method)
        
        # 如果是高密度，加上呼吸练习
        if state.intensity == IntensityType.HIGH:
            breathing_method = self._breathing_exercise()
            methods.append(breathing_method)
        
        # 生成回复
        response_text = self._generate_response(methods)
        
        return StrategyResponse(
            strategy=self.name,
            methods=methods,
            response_text=response_text,
            metadata={
                "problem_type": problem_type,
                "intensity": state.intensity.value
            }
        )
    
    def _initial_empathy(self) -> MethodResult:
        """初始共情"""
        content = (
            "听起来你现在有些困扰，我能理解这种感受。\n"
            "面对这样的情况，确实会让人有些为难。"
        )
        self._log_execution("初始共情")
        return self._create_method_result("初始共情", content)
    
    async def _get_advice_method(self, problem_type: str) -> MethodResult:
        """根据问题类型获取建议方法"""
        method_func = self.problem_methods.get(problem_type, self._general_advice)
        return await method_func()
    
    async def _cognitive_restructuring(self) -> MethodResult:
        """认知重构三问"""
        content = (
            "也许可以问问自己几个问题：\n"
            "1. 有什么证据支持你的担心？回想一下，过去有没有成功的时候？\n"
            "2. 最坏的结果是什么？是不是也没那么可怕？\n"
            "3. 现在能做点什么让情况好一点？哪怕是很小的事。"
        )
        suggestions = [
            "写下你的担心和证据",
            "回想过去成功的经历",
            "列出可以采取的小步骤"
        ]
        self._log_execution("认知重构三问")
        return self._create_method_result("认知重构三问", content, suggestions)
    
    async def _breathing_suggestion(self) -> MethodResult:
        """呼吸法建议"""
        content = (
            "心里烦的时候，可以先做几个深呼吸。\n"
            "不用想那么多，先让自己平静下来。\n"
            "平静了之后，再看怎么解决问题。"
        )
        suggestions = [
            "用鼻子吸气 4 秒",
            "屏住呼吸 4 秒",
            "用嘴呼气 6 秒",
            "重复 3-5 次"
        ]
        self._log_execution("呼吸法建议")
        return self._create_method_result("呼吸法建议", content, suggestions)
    
    async def _small_achievement(self) -> MethodResult:
        """微小成就清单"""
        content = (
            "有时候不想动，就从最小的事开始。\n"
            "比如：\n"
            "• 起床叠好被子\n"
            "• 喝一杯温水\n"
            "• 下楼走 5 分钟\n"
            "做完一件，心里会轻松一点。"
        )
        suggestions = [
            "每天列 3 个小目标",
            "完成后打勾",
            "不要设太高的标准"
        ]
        self._log_execution("微小成就清单")
        return self._create_method_result("微小成就清单", content, suggestions)
    
    async def _sleep_advice(self) -> MethodResult:
        """睡眠建议"""
        content = (
            "睡不好的话，可以试试：\n"
            "• 每天固定时间睡觉起床\n"
            "• 睡前 1 小时别看手机\n"
            "• 卧室暗一点，安静一点\n"
            "• 要是 30 分钟还睡不着，就起来坐会儿"
        )
        suggestions = [
            "建立固定的作息时间",
            "睡前做放松活动",
            "避免咖啡因和酒精"
        ]
        self._log_execution("睡眠建议")
        return self._create_method_result("睡眠建议", content, suggestions)
    
    async def _sun_exposure(self) -> MethodResult:
        """阳光暴露法"""
        content = (
            "今天上午阳光好的时候，出去晒晒太阳吧。\n"
            "就在楼下站一会儿，或者慢慢走一圈。\n"
            "不用戴帽子，让阳光照在脸上。\n"
            "晒 20 分钟就行，对身体和心情都有好处。"
        )
        suggestions = [
            "上午 9-10 点最佳",
            "散步或站立都可以",
            "注意保暖"
        ]
        self._log_execution("阳光暴露法")
        return self._create_method_result("阳光暴露法", content, suggestions)
    
    async def _general_advice(self) -> MethodResult:
        """一般建议"""
        content = (
            "也许可以先想清楚你最在意的是什么。\n"
            "这样会更容易做决定。\n"
            "不用着急，慢慢来。"
        )
        self._log_execution("一般建议")
        return self._create_method_result("一般建议", content)
    
    def _breathing_exercise(self) -> MethodResult:
        """呼吸练习"""
        content = (
            "来，现在跟我一起做几个深呼吸。\n"
            "吸气……4 下\n"
            "屏住……4 下\n"
            "呼气……6 下\n"
            "对，就是这样，再来一次。"
        )
        self._log_execution("呼吸练习")
        return self._create_method_result("呼吸练习", content)
    
    def _generate_response(self, methods: List[MethodResult]) -> str:
        """生成回复"""
        parts = []
        for i, m in enumerate(methods):
            if i == 0:
                parts.append(m.content)
            else:
                parts.append(f"\n{m.content}")
        return "\n\n".join(parts)