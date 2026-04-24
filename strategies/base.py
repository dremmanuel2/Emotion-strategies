"""
策略基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
from loguru import logger

from models import UserInput, StrategyResponse, MethodResult, StateJudgment


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = ""
        self.suitable_emotions: List[str] = []
        self.suitable_stages: List[str] = []
        self.suitable_intensities: List[str] = []
        self.suitable_risks: List[str] = []
        self.methods_info: List[Dict[str, Any]] = []
    
    @abstractmethod
    async def execute(self, user_input: UserInput, state: StateJudgment) -> StrategyResponse:
        """
        执行策略
        
        Args:
            user_input: 用户输入
            state: 状态判断结果
        
        Returns:
            StrategyResponse: 策略响应
        """
        pass
    
    @abstractmethod
    def can_handle(self, user_input: UserInput, state: StateJudgment) -> bool:
        """
        判断是否可以处理该输入
        
        Args:
            user_input: 用户输入
            state: 状态判断结果
        
        Returns:
            bool: 是否可以处理
        """
        pass
    
    def _create_method_result(self, name: str, content: str, suggestions: Optional[List[str]] = None) -> MethodResult:
        """创建方法结果"""
        return MethodResult(
            method_name=name,
            content=content,
            suggestions=suggestions or []
        )
    
    def _log_execution(self, method_name: str, details: Optional[str] = None):
        """记录执行日志"""
        logger.info(f"[{self.name}] 执行方法：{method_name}")
        if details:
            logger.debug(f"[{self.name}] 详情：{details}")