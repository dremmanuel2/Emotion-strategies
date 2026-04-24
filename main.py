"""
情感陪伴策略系统 API
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys
from pathlib import Path

from models import UserInput, StrategyResponse, StateJudgment
from strategy_manager import StrategyManager
from config import get_settings
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

# 配置日志
log_file = Path("logs/app.log")
log_file.parent.mkdir(exist_ok=True)

logger.remove()
logger.add(
    sys.stdout,
    level=get_settings().LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)
logger.add(
    str(log_file),
    level=get_settings().LOG_LEVEL,
    rotation="500 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
)

# 创建 FastAPI 应用
app = FastAPI(
    title="情感陪伴策略系统",
    description="基于心理学知识库的老年人情感陪伴 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化策略管理器
strategy_manager = StrategyManager()


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("=" * 50)
    logger.info("情感陪伴策略系统启动")
    logger.info(f"版本：1.0.0")
    logger.info(f"策略数量：{len(strategy_manager.strategies)}")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("情感陪伴策略系统关闭")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "情感陪伴策略系统",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/api/v1/emotion/respond", response_model=StrategyResponse)
async def emotion_respond(user_input: UserInput, use_agent: bool = True):
    """
    情感响应接口

    根据用户输入的情绪和状态，生成合适的情感陪伴响应。
    """
    try:
        logger.info(f"收到请求 | 文本：{user_input.text[:50]}... | 情绪：{user_input.emotion.value} | 智能体：{use_agent}")

        if not user_input.stage:
            user_input.stage = "neutral"
        if not user_input.intensity:
            user_input.intensity = "low"
        if not user_input.risk:
            user_input.risk = "low"

        from models import StageType, IntensityType, RiskType
        state = StateJudgment(
            stage=StageType(user_input.stage),
            intensity=IntensityType(user_input.intensity),
            risk=RiskType(user_input.risk)
        )

        response = await strategy_manager.select_and_execute(user_input, state)

        logger.info(f"响应生成成功 | 策略：{response.strategy}")
        return response

    except Exception as e:
        logger.error(f"处理请求失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/state/judge")
async def judge_state(text: str, emotion: str = "neutral"):
    """状态判断接口（规则版 fallback）"""
    from models import StageType, IntensityType, RiskType

    try:
        stage = "neutral"
        intensity = "low"
        risk = "low"

        risk_keywords = ["不想活", "活着没意义", "想死", "绝望", "没意思", "活不下去"]
        if any(keyword in text for keyword in risk_keywords):
            risk = "high"

        help_keywords = ["怎么办", "怎么做", "如何", "应该", "帮帮我"]
        if any(keyword in text for keyword in help_keywords):
            stage = "help"
            intensity = "medium"

        venting_keywords = ["气死我了", "好难过", "烦死了", "不开心", "难受"]
        if any(keyword in text for keyword in venting_keywords):
            stage = "venting"
            intensity = "medium"

        if "!" in text or "!!" in text or "!!!" in text:
            intensity = "high"
        elif "?" in text and stage == "help":
            intensity = "medium"

        return {
            "stage": stage,
            "intensity": intensity,
            "risk": risk
        }

    except Exception as e:
        logger.error(f"状态判断失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/strategies")
async def list_strategies():
    """获取所有可用策略"""
    return {
        "strategies": strategy_manager.get_strategy_info()
    }


@app.get("/api/v1/hotlines")
async def get_hotlines():
    """获取心理援助热线"""
    settings = get_settings()
    return {
        "hotlines": [
            {"name": "全国希望 24 热线", "number": settings.HOTLINE_HOPE, "hours": "24 小时"},
            {"name": "全国心理援助热线", "number": settings.HOTLINE_NATIONAL, "hours": "24 小时"},
            {"name": "北京市心理援助热线", "number": settings.HOTLINE_BEIJING, "hours": "工作时间"},
        ]
    }


class ChatRequest(BaseModel):
    """聊天请求"""
    text: str = Field(..., description="用户输入文本")
    session_id: Optional[str] = Field(None, description="会话 ID（用于上下文）")
    api_key: Optional[str] = Field(None, description="硅基流动 API Key")
    model: Optional[str] = Field(None, description="硅基流动模型名称")


class ChatResponse(BaseModel):
    """聊天响应"""
    session_id: str = Field(..., description="会话 ID")
    response_text: str = Field(..., description="助手回复")
    emotion: str = Field(..., description="情绪分析")
    strategy: str = Field(..., description="使用的策略")
    state: Dict[str, str] = Field(..., description="状态分析")
    history_length: int = Field(..., description="当前对话历史长度")


@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    """聊天接口（支持上下文）"""
    try:
        from llm_agents import AgentOrchestrator, ResponseGenerationAgent
        from models import EmotionType, StageType, IntensityType, RiskType, StateJudgment, MethodResult

        conversation = strategy_manager.get_or_create_conversation(request.session_id)
        session_id = conversation.session_id

        strategy_manager.add_to_history(
            session_id,
            role="user",
            content=request.text
        )

        orchestrator = AgentOrchestrator(api_key=request.api_key, model=request.model)
        strategies_info = strategy_manager.get_strategy_for_agent()

        analysis = await orchestrator.process(
            text=request.text,
            context={},
            available_strategies=strategies_info,
            conversation_history=conversation
        )

        emotion = analysis["emotion"]
        state = analysis["state"]
        strategy_name = analysis["selected_strategy"]

        user_input = UserInput(
            text=request.text,
            emotion=emotion
        )

        selected_strategy = None
        for strategy in strategy_manager.strategies:
            if strategy.name == strategy_name:
                selected_strategy = strategy
                break

        if not selected_strategy:
            for strategy in strategy_manager.strategies:
                if strategy.can_handle(user_input, state):
                    selected_strategy = strategy
                    break

        if selected_strategy:
            response = await selected_strategy.execute(user_input, state)
        else:
            response = await strategy_manager._default_response(user_input, state)

        try:
            response_agent = ResponseGenerationAgent(api_key=request.api_key, model=request.model)
            method_results = [
                {"method_name": m.method_name, "content": m.content}
                for m in response.methods
            ]
            optimized_text = await response_agent.generate(
                text=request.text,
                emotion=emotion,
                state=state,
                strategy_name=strategy_name,
                method_results=method_results,
                conversation_history=conversation
            )
            response.response_text = optimized_text
        except Exception as e:
            logger.warning(f"[chat] 响应优化失败，使用原始回复：{e}")

        strategy_manager.add_to_history(
            session_id,
            role="assistant",
            content=response.response_text,
            emotion=emotion.value,
            strategy=strategy_name
        )

        return ChatResponse(
            session_id=session_id,
            response_text=response.response_text,
            emotion=emotion.value,
            strategy=strategy_name,
            state={
                "stage": state.stage.value,
                "intensity": state.intensity.value,
                "risk": state.risk.value
            },
            history_length=len(conversation.messages)
        )

    except Exception as e:
        logger.error(f"聊天接口失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/history/{session_id}")
async def get_history(session_id: str, limit: int = 20):
    """获取对话历史"""
    conversation = strategy_manager.get_history(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    messages = conversation.get_recent_messages(limit)
    return {
        "session_id": conversation.session_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "emotion": msg.emotion,
                "strategy": msg.strategy
            }
            for msg in messages
        ],
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "total_messages": len(conversation.messages)
    }


@app.delete("/api/v1/history/{session_id}")
async def clear_history(session_id: str):
    """清空对话历史"""
    if session_id in strategy_manager.conversations:
        del strategy_manager.conversations[session_id]
        logger.info(f"[api] 已清空会话历史：{session_id}")
        return {"success": True, "message": "对话历史已清空"}
    else:
        raise HTTPException(status_code=404, detail="会话不存在")


@app.post("/api/v1/agent/analyze")
async def agent_analyze(text: str, context: Optional[Dict[str, Any]] = None, api_key: Optional[str] = None):
    """智能体完整分析接口"""
    try:
        from llm_agents import AgentOrchestrator

        orchestrator = AgentOrchestrator(api_key=api_key)
        strategies_info = strategy_manager.get_strategy_for_agent()

        result = await orchestrator.process(
            text=text,
            context=context,
            available_strategies=strategies_info
        )

        return {
            "emotion": {
                "type": result["emotion"].value,
            },
            "state": {
                "stage": result["state"].stage.value,
                "intensity": result["state"].intensity.value,
                "risk": result["state"].risk.value
            },
            "selected_strategy": result["selected_strategy"],
            "success": True
        }

    except Exception as e:
        logger.error(f"智能体分析失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/agent/full_respond")
async def agent_full_respond(
        text: str,
        context: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None
):
    """智能体完整响应接口"""
    try:
        from llm_agents import AgentOrchestrator, ResponseGenerationAgent
        from models import EmotionType, StageType, IntensityType, RiskType, StateJudgment, MethodResult

        orchestrator = AgentOrchestrator(api_key=api_key)
        strategies_info = strategy_manager.get_strategy_for_agent()

        analysis = await orchestrator.process(
            text=text,
            context=context,
            available_strategies=strategies_info
        )

        emotion = analysis["emotion"]
        state = analysis["state"]
        strategy_name = analysis["selected_strategy"]

        user_input = UserInput(
            text=text,
            emotion=emotion,
            context=context or {}
        )

        selected_strategy = None
        for strategy in strategy_manager.strategies:
            if strategy.name == strategy_name:
                selected_strategy = strategy
                break

        if not selected_strategy:
            for strategy in strategy_manager.strategies:
                if strategy.can_handle(user_input, state):
                    selected_strategy = strategy
                    break

        if selected_strategy:
            response = await selected_strategy.execute(user_input, state)
        else:
            response = await strategy_manager._default_response(user_input, state)

        try:
            response_agent = ResponseGenerationAgent(api_key=api_key)
            method_results = [
                {"method_name": m.method_name, "content": m.content}
                for m in response.methods
            ]
            optimized_text = await response_agent.generate(
                text=text,
                emotion=emotion,
                state=state,
                strategy_name=strategy_name,
                method_results=method_results
            )
            response.response_text = optimized_text
            logger.info(f"[agent_full_respond] 响应优化完成")
        except Exception as e:
            logger.warning(f"[agent_full_respond] 响应优化失败，使用原始回复：{e}")

        return {
            "emotion": emotion.value,
            "state": {
                "stage": state.stage.value,
                "intensity": state.intensity.value,
                "risk": state.risk.value
            },
            "strategy": strategy_name,
            "response_text": response.response_text,
            "methods": [
                {
                    "method_name": m.method_name,
                    "content": m.content,
                    "suggestions": m.suggestions
                }
                for m in response.methods
            ],
            "success": True
        }

    except Exception as e:
        logger.error(f"智能体完整响应失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )