"""
引导倾诉策略 - 帮助用户表达情绪
"""
from typing import List
from loguru import logger

from models import UserInput, StrategyResponse, MethodResult, StateJudgment, StageType
from strategies.base import BaseStrategy


class VentingSupportStrategy(BaseStrategy):
    """引导倾诉策略"""
    
    def __init__(self):
        super().__init__()
        self.name = "VENTING_SUPPORT"
        self.description = "【倾诉引导】针对情绪发泄状态的用户，通过表达倾听意愿、开放式引导和安抚话术帮助用户充分表达情绪"
        self.suitable_emotions = ["sad", "angry", "anxious"]
        self.suitable_stages = ["venting"]
        self.suitable_intensities = ["high"]
        self.suitable_risks = ["low"]
        self.methods_info = [
            {"name": "表达倾听意愿", "desc": "邀请用户多说一些，表达真诚的倾听态度"},
            {"name": "开放式引导", "desc": "使用非评判性的语言鼓励用户自由表达"},
            {"name": "安抚话术", "desc": "告知用户倾诉的积极意义，减轻心理负担"}
        ]
        
        # 跟进方法
        self.followup_methods = {
            "回忆往事": self._memory_followup,
            "抱怨现状": self._complaint_followup,
            "担忧健康": self._health_worry_followup,
            "思念亲人": self._missing_followup,
            "default": self._default_followup
        }
    
    def can_handle(self, user_input: UserInput, state: StateJudgment) -> bool:
        """发泄状态使用此策略"""
        return state.stage == StageType.VENTING and state.intensity.value == "high"
    
    async def execute(self, user_input: UserInput, state: StateJudgment) -> StrategyResponse:
        """执行引导倾诉策略"""
        logger.info(f"[{self.name}] 执行引导倾诉策略")
        
        methods: List[MethodResult] = []
        
        # 表达倾听意愿
        listen_method = self._express_willingness_to_listen()
        methods.append(listen_method)
        
        # 开放式引导
        open_question_method = self._open_ended_guidance()
        methods.append(open_question_method)
        
        # 安抚话术
        comfort_method = self._comfort_words()
        methods.append(comfort_method)
        
        # 生成回复
        response_text = self._generate_response(methods)
        
        return StrategyResponse(
            strategy=self.name,
            methods=methods,
            response_text=response_text,
            metadata={
                "stage": "venting",
                "followup_needed": True
            }
        )
    
    def _express_willingness_to_listen(self) -> MethodResult:
        """表达倾听意愿"""
        content = (
            "你愿意多说说最近发生了什么吗？\n"
            "我在这儿听着呢。"
        )
        self._log_execution("表达倾听意愿")
        return self._create_method_result("表达倾听意愿", content)
    
    def _open_ended_guidance(self) -> MethodResult:
        """开放式引导"""
        content = (
            "不用着急，慢慢说。\n"
            "想到什么就说什么，没有对错。"
        )
        self._log_execution("开放式引导")
        return self._create_method_result("开放式引导", content)
    
    def _comfort_words(self) -> MethodResult:
        """安抚话术"""
        content = (
            "把事情说出来，心里可能会轻松一点。\n"
            "我会一直在这儿听你说。"
        )
        self._log_execution("安抚话术")
        return self._create_method_result("安抚话术", content)
    
    async def followup(self, user_input: UserInput, context: str = "default") -> MethodResult:
        """根据内容跟进"""
        followup_func = self.followup_methods.get(context, self._default_followup)
        return await followup_func(user_input)
    
    async def _memory_followup(self, user_input: UserInput) -> MethodResult:
        """回忆往事跟进"""
        content = (
            "你刚才说以前……那段时光听起来很美好。\n"
            "要不要多跟我讲讲那时候的事？\n"
            "说说你记得最清楚的是什么？"
        )
        self._log_execution("回忆往事跟进")
        return self._create_method_result("回忆往事跟进", content)
    
    async def _complaint_followup(self, user_input: UserInput) -> MethodResult:
        """抱怨现状跟进"""
        content = (
            "听起来现在的情况确实让你不太满意。\n"
            "你最希望改变的是哪一方面呢？\n"
            "有没有什么事情是现在就能做，让情况好一点点的？"
        )
        self._log_execution("抱怨现状跟进")
        return self._create_method_result("抱怨现状跟进", content)
    
    async def _health_worry_followup(self, user_input: UserInput) -> MethodResult:
        """担忧健康跟进"""
        content = (
            "你担心身体，这种心情我能理解。\n"
            "有时候越想越害怕，反而更紧张。\n"
            "咱们先不想那么多，说说你现在感觉怎么样？\n"
            "有没有哪里不舒服？"
        )
        self._log_execution("担忧健康跟进")
        return self._create_method_result("担忧健康跟进", content)
    
    async def _missing_followup(self, user_input: UserInput) -> MethodResult:
        """思念亲人跟进"""
        content = (
            "听你这么说，你很想他/她吧。\n"
            "要是愿意的话，可以跟我讲讲他/她的事。\n"
            "你们在一起的时候，有什么开心的回忆？"
        )
        self._log_execution("思念亲人跟进")
        return self._create_method_result("思念亲人跟进", content)
    
    async def _default_followup(self, user_input: UserInput) -> MethodResult:
        """默认跟进"""
        content = (
            "我在这里听着呢。\n"
            "你继续说，我在听。"
        )
        self._log_execution("默认跟进")
        return self._create_method_result("默认跟进", content)
    
    def _generate_response(self, methods: List[MethodResult]) -> str:
        """生成回复"""
        parts = [m.content for m in methods]
        return "\n\n".join(parts)