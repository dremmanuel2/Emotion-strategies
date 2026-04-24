"""
策略模块
"""
from strategies.base import BaseStrategy
from strategies.safety import SafetyStrategy
from strategies.empathy import EmpathyStrategy
from strategies.venting import VentingSupportStrategy
from strategies.guidance import GuidanceLightStrategy
from strategies.breathing import BreathingStrategy
from strategies.music import MusicOfferStrategy
from strategies.interest import InterestRedirectStrategy
from strategies.joy import JoyShareStrategy
from strategies.company import CompanyStrategy

__all__ = [
    "BaseStrategy",
    "SafetyStrategy",
    "EmpathyStrategy",
    "VentingSupportStrategy",
    "GuidanceLightStrategy",
    "BreathingStrategy",
    "MusicOfferStrategy",
    "InterestRedirectStrategy",
    "JoyShareStrategy",
    "CompanyStrategy",
]