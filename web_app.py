"""
情感陪伴策略系统 - Web 对话界面
使用 Streamlit 框架 + 大模型情感识别
"""
import streamlit as st
import asyncio
import httpx
from datetime import datetime
import json

# 设置页面配置
st.set_page_config(
    page_title="情感陪伴助手",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API 配置
API_BASE_URL = "http://100.100.30.150:8531"

# 自定义 CSS 样式
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
    }
    .chat-user {
        background-color: #e3f2fd;
    }
    .chat-assistant {
        background-color: #f5f5f5;
    }
    .analysis-box {
        background-color: #fff3e0;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ff9800;
        margin: 10px 0;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = ""


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("⚙️ 设置")
        
        # API 配置
        api_url = st.text_input(
            "API 地址",
            value=st.session_state.get("api_url", API_BASE_URL),
            key="api_url_input"
        )
        st.session_state.api_url = api_url
        
        # 硅基流动配置
        st.subheader("🤖 智能体配置")
        api_key = st.text_input(
            "API Key",
            type="password",
            value="",
            key="silicon_api_key_input",
            help="获取：https://cloud.siliconflow.cn/ | 留空则使用.env 中的配置"
        )
        st.session_state.silicon_api_key = api_key
        
        # 模型选择
        model_options = [
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-32B-Instruct",
            "Qwen/Qwen2.5-14B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "deepseek-ai/DeepSeek-V3",
            "deepseek-ai/DeepSeek-R1",
            "THUDM/glm-4-9b-chat",
            "01-ai/Yi-1.5-34B-Chat",
            "01-ai/Yi-1.5-9B-Chat",
            "meta-llama/Llama-3.3-70B-Instruct",
            "meta-llama/Llama-3.1-8B-Instruct",
            "internlm/internlm2_5-7b-chat",
            "zhipuai/ChatGLM3-6B"
        ]
        selected_model = st.selectbox(
            "选择模型",
            options=model_options,
            index=0,
            key="model_select",
            help="选择硅基流动的推理模型"
        )
        st.session_state.silicon_model = selected_model
        
        st.info("✅ 使用多智能体系统进行情绪、状态、风险分析和策略选择")
        
        st.divider()
        
        # 操作按钮
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.session_state.session_id = ""
            st.rerun()
        
        # 显示当前会话 ID
        if st.session_state.session_id:
            st.markdown(f"**会话 ID**: `{st.session_state.session_id[:8]}...`")
        
        if st.button("🔄 新建会话", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.session_state.session_id = ""
            st.rerun()
        
        if st.button("💾 导出对话", use_container_width=True):
            if st.session_state.conversation_history:
                export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "conversation": st.session_state.conversation_history
                }
                json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📥 下载",
                    data=json_str,
                    file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        st.divider()
        st.markdown("**📞 心理援助热线**")
        st.markdown("• 全国希望 24 热线：400-161-9995")
        st.markdown("• 北京市心理援助：010-82951332")


async def analyze_with_llm_old(text: str, api_key: str, model: str, base_url: str) -> dict:
    """使用大模型分析情绪和状态（旧版，保留作为 fallback）"""
    # 此函数已不再使用，保留作为备份
    pass


async def send_message(user_input: str, base_url: str):
    """发送消息并获取响应（使用智能体系统 + 上下文）"""
    try:
        # 获取配置
        api_key = st.session_state.get("silicon_api_key", "")
        session_id = st.session_state.get("session_id", "")
        model = st.session_state.get("silicon_model", "Qwen/Qwen2.5-72B-Instruct")
        
        # 使用聊天接口（支持上下文）
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "text": user_input
            }
            if session_id:
                payload["session_id"] = session_id
            if api_key:
                payload["api_key"] = api_key
            if model:
                payload["model"] = model
            
            response = await client.post(
                f"{base_url}/api/v1/chat",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 保存 session_id
                st.session_state.session_id = result["session_id"]
                
                analysis = {
                    "emotion": result.get("emotion", "neutral"),
                    "stage": "N/A",
                    "intensity": "N/A",
                    "risk": "N/A",
                    "strategy": result.get("strategy", "EmpathyStrategy")
                }
                return {
                    "response": result["response_text"],
                    "strategy": result["strategy"],
                    "methods": [],
                    "analysis": analysis,
                    "session_id": result["session_id"],
                    "history_length": result.get("history_length", 0)
                }
            else:
                st.error(f"API 错误：{response.status_code}")
                return None
                
    except Exception as e:
        st.error(f"发送消息失败：{str(e)}")
        return None


def main():
    """主函数"""
    init_session_state()
    render_sidebar()
    
    st.title("💙 情感陪伴助手")
    st.markdown("🤖 多智能体情感分析 | 💬 支持上下文连贯对话")
    
    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 聊天输入
    if user_input := st.chat_input("请输入您想说的话..."):
        # 添加用户消息
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # 获取配置
        api_url = st.session_state.get("api_url", API_BASE_URL)
        
        # 获取 AI 响应
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                result = asyncio.run(send_message(user_input, api_url))
                
                if result:
                    st.markdown(result["response"])
                    
                    # 显示分析详情
                    with st.expander("📊 查看智能体分析详情"):
                        analysis = result["analysis"]
                        cols = st.columns(4)
                        cols[0].metric("情绪", analysis.get("emotion", "N/A"))
                        cols[1].metric("策略", result["strategy"])
                        cols[2].metric("会话长度", result.get("history_length", 0))
                        cols[3].metric("会话 ID", st.session_state.session_id[:8] + "...")
                        
                        st.markdown(f"""
                        <div class="analysis-box">
                            <strong>🤖 智能体分析结果：</strong><br>
                            情绪类型：{analysis.get("emotion")} |
                            使用策略：{result["strategy"]}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if result.get("methods"):
                            st.markdown("**📋 执行的方法：**")
                            for method in result["methods"]:
                                st.markdown(f"- **{method['method_name']}**: {method['content'][:100]}...")
                    
                    # 保存消息
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["response"]
                    })
                    
                    # 保存对话历史
                    st.session_state.conversation_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "user": user_input,
                        "assistant": result["response"],
                        "analysis": result["analysis"]
                    })
                else:
                    st.error("抱歉，我遇到了一些问题，请稍后再试。")
    
    # 页脚
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 13px;">
        💙 情感陪伴助手 | 如有紧急情况请联系专业机构
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()