"""
配置管理
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8501
    DEBUG: bool = False
    
    # 硅基流动 LLM 配置
    SILICONFLOW_API_KEY: str = "sk-bamdxwcpuztjvausmdbrawauilfyxfyzsthnjxjeawhauset"
    SILICONFLOW_API_BASE_URL: str = "https://api.siliconflow.cn/v1"
    SILICONFLOW_MODEL: str = "Qwen/Qwen2.5-72B-Instruct"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # 心理援助热线
    HOTLINE_NATIONAL: str = "400-161-9995"
    HOTLINE_BEIJING: str = "010-82951332"
    HOTLINE_HOPE: str = "400-161-9995"
    
    # class Config:
    #     env_file = ".env"
    #     case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()