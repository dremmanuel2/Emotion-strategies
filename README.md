# 情感陪伴助手 - 多智能体版

> 🤖 基于大模型智能体的情感陪伴系统 | 自然对话 | 专业陪伴 | **支持上下文连贯对话**

## ✨ 核心特性

- **🤖 多智能体系统**：4 个专业智能体协同工作（情绪分析、状态分析、策略选择、响应生成）
- **🎯 大模型情感识别**：使用硅基流动 Qwen2.5-72B 深度理解用户情绪
- **💙 9 种陪伴策略**：安全干预、共情、倾诉引导、建议、呼吸练习、音乐推荐等
- **🔗 上下文记忆**：自动管理对话历史，智能体记住之前聊过的内容
- **🌐 Web 对话界面**：简洁美观，实时显示智能体分析结果
- **⚡ 异步架构**：FastAPI + async/await，高性能响应

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- 硅基流动 API Key（获取：https://cloud.siliconflow.cn/）

### 2. 安装依赖

```bash
# 激活虚拟环境
D:\anaconda3\envs\py313\activate

# 进入项目目录
cd E:\AI\ZJU_BJ\CUIBO\AffectCompanyAgent\emotion_strategies

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 API Key

编辑 `.env` 文件：

```bash
# 硅基流动 API 配置
SILICONFLOW_API_KEY=sk-your-api-key-here
SILICONFLOW_API_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=Qwen/Qwen2.5-72B-Instruct

# 服务配置
HOST=0.0.0.0
PORT=8501
DEBUG=false
```

### 4. 启动服务

**方式 1：使用启动脚本**
```bash
start_web.bat
```

**方式 2：手动启动（推荐）**

终端 1 - 启动后端 API：
```bash
D:\anaconda3\envs\py313\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8501
```

终端 2 - 启动 Web 界面：
```bash
D:\anaconda3\envs\py313\python.exe -m streamlit run web_app.py --server.address=localhost --server.port=8502
```

### 5. 访问

| 服务 | 地址 |
|------|------|
| **Web 界面** | http://100.100.30.150:8502 |
| **API 文档** | http://100.100.30.150/docs |
| **测试页面** | 直接打开 `test_page.html` |

---

## 🤖 多智能体架构

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户输入                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         EmotionAnalysisAgent (情绪分析智能体)                │
│         分析用户情绪类型 (sad/angry/anxious/neutral)         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         StateAnalysisAgent (状态分析智能体)                  │
│         分析状态阶段、强度、风险                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         StrategySelectionAgent (策略选择智能体)              │
│         根据状态和情绪选择合适的策略                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         策略执行 (BaseStrategy)                              │
│         执行具体的陪伴方法                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         ResponseGenerationAgent (响应生成智能体)             │
│         生成自然、温暖的最终回复                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      输出响应                                │
└─────────────────────────────────────────────────────────────┘
```

### 智能体角色

| 智能体 | 职责 | 输出 |
|--------|------|------|
| **EmotionAnalysisAgent** | 深度分析情绪状态 | sad/angry/anxious/neutral/positive |
| **StateAnalysisAgent** | 分析心理状态 | stage/intensity/risk |
| **StrategySelectionAgent** | 选择合适的陪伴策略 | 策略名称 |
| **ResponseGenerationAgent** | 优化回复质量 | 自然温暖的文本 |

---

## 📋 策略详细说明

### 策略选择决策树

```
1. 风险等级 = high？
   └─ 是 → SAFETY（安全干预）
   └─ 否 → 继续判断

2. 情绪 = positive？
   └─ 是 → JOY_SHARE（喜悦分享）或 MUSIC_OFFER（音乐推荐）
   └─ 否 → 继续判断

3. 状态阶段 = venting（发泄）？
   ├─ 强度 = high → VENTING_SUPPORT（倾诉引导）
   ├─ 强度 = medium/low → EMPATHY（共情）或 MUSIC_OFFER（音乐推荐）
   └─ 否 → 继续判断

4. 状态阶段 = help（求助）？
   ├─ 强度 = high → GUIDANCE_LIGHT（温和建议）+ BREATHING（呼吸练习）
   ├─ 强度 = medium → GUIDANCE_LIGHT（温和建议）或 INTEREST_REDIRECT（兴趣转移）
   └─ 强度 = low → INTEREST_REDIRECT（兴趣转移）

5. 情绪 = anxious（焦虑）且 强度 >= medium？
   └─ 是 → BREATHING（呼吸练习）优先
   └─ 否 → 继续判断

6. 情绪 = neutral 且 状态 = neutral？
   └─ 是 → COMPANY（日常陪伴）或 INTEREST_REDIRECT（兴趣转移）
   └─ 否 → EMPATHY（共情）
```

### 策略列表

| 策略 | 代码名 | 适用情绪 | 适用状态 | 适用强度 | 功能描述 |
|------|--------|----------|----------|----------|----------|
| **安全干预** | `SAFETY` | 所有 | 所有 | high | ⚠️ 高风险紧急干预，提供心理援助热线 |
| **共情陪伴** | `EMPATHY` | sad/anxious/angry | venting/neutral | all | 💙 理解接纳情绪，情感确认和陪伴 |
| **倾诉引导** | `VENTING_SUPPORT` | sad/angry/anxious | venting | high | 🗣️ 引导充分表达，情绪释放 |
| **温和建议** | `GUIDANCE_LIGHT` | all | help | all | 💡 先共情后建议，问题解决导向 |
| **呼吸练习** | `BREATHING` | anxious/sad | venting/help | medium/high | 🧘 结构化呼吸法（4-7-8/5-5-5/方块/身体扫描） |
| **音乐推荐** | `MUSIC_OFFER` | sad/anxious/angry/positive | venting/neutral | low/medium | 🎵 根据情绪推荐老歌和纯音乐 |
| **兴趣转移** | `INTEREST_REDIRECT` | all | help/neutral | low/medium | 🌻 转移注意力到积极活动（养花/太极/书法等） |
| **喜悦分享** | `JOY_SHARE` | positive | all | all | 😊 分享喜悦，正向强化积极情绪 |
| **日常陪伴** | `COMPANY` | neutral | neutral | low/medium | ☕ 日常聊天，根据上下文提供陪伴 |

### 策略方法详情

每个策略包含多个方法，智能体会根据具体情况选择：

#### 1. SAFETY - 安全干预策略
- **表达关心**：表达对用户安全的担忧和关心
- **建议寻求现实帮助**：鼓励联系信任的人或专业心理咨询师
- **提供心理援助热线**：提供全国和地区心理援助热线

#### 2. EMPATHY - 共情策略
- **情绪共情**：根据情绪类型提供针对性理解
- **经历认可**：认可感受的真实性，消除自责
- **陪伴表达**：表达陪伴意愿

#### 3. VENTING_SUPPORT - 倾诉引导策略
- **表达倾听意愿**：邀请用户多说一些
- **开放式引导**：非评判性鼓励自由表达
- **安抚话术**：告知倾诉的积极意义

#### 4. GUIDANCE_LIGHT - 轻建议策略
- **初始共情**：先表达理解
- **认知重构三问**：引导反思（适用于决策问题）
- **呼吸法建议**：建议深呼吸平复情绪
- **微小成就清单**：提供简单易行的小目标
- **睡眠建议**：睡眠卫生习惯
- **阳光暴露法**：建议户外晒太阳

#### 5. BREATHING - 呼吸引导策略
- **4-7-8 呼吸法**：急性焦虑发作
- **5-5-5 呼吸法**：日常使用，适合老年人
- **方块呼吸法**：配合视觉焦点，悲伤情绪
- **身体扫描呼吸法**：睡前放松

#### 6. MUSIC_OFFER - 音乐推荐策略
- **询问音乐偏好**：根据情绪调整询问方式
- **推荐歌曲**：从歌曲库选择 3 首适合的歌曲

#### 7. INTEREST_REDIRECT - 兴趣转移策略
- **微小成就清单**：简单小目标（适用于悲伤）
- **日常掌控清单**：规律日常活动（适用于焦虑）
- **兴趣话题探索**：老年人兴趣爱好（适用于愤怒/日常）
- **日常陪伴**：日常问候关心

#### 8. JOY_SHARE - 喜悦分享策略
- **分享喜悦**：表达为用户高兴
- **鼓励听音乐**：高强度时推荐欢快老歌
- **鼓励记录**：中强度时鼓励记录美好
- **微休息建议**：低强度时建议休息

#### 9. COMPANY - 日常陪伴策略
- **日常问候**：询问当天情况
- **微休息练习**：针对疲劳状态
- **兴趣话题探索**：针对无聊状态
- **倾听陪伴**：针对想聊天状态
- **情绪急救包建议**：针对独居状态
- **睡眠卫生建议**：针对睡眠问题

📖 **详细策略文档**: 查看 [`strategies/STRATEGY_GUIDE.md`](strategies/STRATEGY_GUIDE.md)

---

## 🔌 API 接口

### 1. 聊天接口（推荐，支持上下文）

```bash
POST http://100.100.30.150/api/v1/chat
```

**请求体：**
```json
{
  "text": "我今天心情很不好",
  "session_id": "可选 - 会话 ID",
  "api_key": "可选-API Key"
}
```

**返回示例：**
```json
{
  "session_id": "abc-123-def",
  "response_text": "我能感受到你现在很难过...",
  "emotion": "sad",
  "strategy": "EMPATHY",
  "state": {
    "stage": "venting",
    "intensity": "medium",
    "risk": "low"
  },
  "history_length": 2
}
```

### 2. 获取对话历史

```bash
GET http://100.100.30.150/api/v1/history/{session_id}?limit=20
```

### 3. 清空对话历史

```bash
DELETE http://100.100.30.150/api/v1/history/{session_id}
```

### 4. 智能体完整响应（无上下文）

```bash
POST http://100.100.30.150/api/v1/agent/full_respond
```

### 5. 获取策略信息

```bash
GET http://100.100.30.150/api/v1/strategies
```

返回所有策略的详细信息（包含适用条件和方法列表）。

---

## 💻 使用示例

### Python 调用（带上下文）

```python
import httpx
import asyncio

async def test_chat():
    async with httpx.AsyncClient() as client:
        # 第一轮对话
        response1 = await client.post(
            "http://100.100.30.150/api/v1/chat",
            json={"text": "我今天心情很不好，感觉很烦"}
        )
        result1 = response1.json()
        print(f"回复 1: {result1['response_text']}")
        print(f"会话 ID: {result1['session_id']}")
        
        # 第二轮对话（带上下文）
        response2 = await client.post(
            "http://100.100.30.150/api/v1/chat",
            json={
                "text": "因为和同事吵架了",
                "session_id": result1["session_id"]
            }
        )
        result2 = response2.json()
        print(f"回复 2: {result2['response_text']}")
        # 智能体会记住之前聊过"心情不好"，能理解"同事吵架"是原因

asyncio.run(test_chat())
```

### cURL 调用

```bash
# 第一轮对话
curl -X POST http://100.100.30.150/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "我今天心情很不好"}'

# 第二轮对话（带会话 ID）
curl -X POST http://100.100.30.150/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "因为和同事吵架了", "session_id": "abc-123"}'
```

---

## 🧪 测试场景

| 用户输入 | 预期分析 | 选择策略 |
|----------|----------|----------|
| "我不想活了，活着太累" | risk=high | **SAFETY** |
| "气死我了！他怎么能这样！" | angry, venting, high | **VENTING_SUPPORT** |
| "最近睡不着，怎么办？" | anxious, help, medium | **GUIDANCE_LIGHT** |
| "我好焦虑，心慌" | anxious, high | **BREATHING** |
| "今天中了奖，好开心！" | positive, high | **JOY_SHARE** |
| "今天天气不错" | neutral, neutral | **COMPANY** |
| "有点失落，提不起精神" | sad, venting, low | **MUSIC_OFFER** |
| "什么都不想做，好无聊" | sad, help, low | **INTEREST_REDIRECT** |

---

## 📁 项目结构

```
emotion_strategies/
├── main.py                      # FastAPI 主应用
├── config.py                    # 配置管理
├── models.py                    # 数据模型
├── strategy_manager.py          # 策略管理器（会话管理）
├── llm_agents.py                # 多智能体系统 ⭐
├── web_app.py                   # Web 界面 (Streamlit)
├── test_page.html               # 测试页面
├── strategy_selection_example.py # 策略选择示例代码
├── .env                         # 环境配置
├── requirements.txt             # 依赖列表
├── start_web.bat                # 启动脚本
└── strategies/                  # 策略模块
    ├── base.py                  # 策略基类
    ├── safety.py                # 安全干预 ⚠️
    ├── empathy.py               # 共情策略 💙
    ├── venting.py               # 引导倾诉 🗣️
    ├── guidance.py              # 轻建议 💡
    ├── breathing.py             # 呼吸引导 🧘
    ├── music.py                 # 音乐推荐 🎵
    ├── interest.py              # 兴趣转移 🌻
    ├── joy.py                   # 喜悦分享 😊
    ├── company.py               # 日常陪伴 ☕
    └── STRATEGY_GUIDE.md        # 策略详细文档 📖
```

---

## 🛡️ 降级策略

如果 LLM 服务不可用，系统会自动降级到规则模式：

1. 智能体初始化失败 → 使用规则模式
2. 智能体分析超时 → 使用规则模式
3. 智能体分析失败 → 使用规则模式

确保系统始终可用。

---

## 📞 心理援助热线

> ⚠️ 如有紧急情况，请立即联系专业机构

| 热线 | 电话 | 服务时间 |
|------|------|----------|
| 全国希望 24 热线 | 400-161-9995 | 24 小时 |
| 全国心理援助热线 | 400-161-9995 | 24 小时 |
| 北京市心理援助热线 | 010-82951332 | 工作时间 |

---

## 🛠️ 技术栈

- **后端**: FastAPI + Uvicorn
- **前端**: Streamlit / HTML
- **LLM**: 硅基流动 Qwen2.5-72B-Instruct
- **异步**: asyncio + httpx
- **数据验证**: Pydantic

---

## 📝 常见问题

### Q: 为什么智能体分析很慢？
A: 首次调用可能需要 3-5 秒（LLM 推理时间），后续会更快。可以使用更小的模型如 Qwen2.5-7B-Instruct。

### Q: 没有 API Key 能用吗？
A: 可以，系统会自动降级到规则模式，但分析准确度会降低。

### Q: 可以自定义策略吗？
A: 可以，继承 `BaseStrategy` 类并添加到 `StrategyManager` 中。

### Q: 如何查看智能体分析详情？
A: 在 Web 界面点击"📊 查看智能体分析详情"展开详细信息。

### Q: 上下文能记住多少轮对话？
A: 默认保留最近 20 条消息（10 轮对话），可以在 `ConversationHistory` 中调整 `max_messages` 参数。

### Q: 会话 ID 需要自己管理吗？
A: 不需要。第一次调用 `/api/v1/chat` 时会自动生成会话 ID，后续请求带上返回的 `session_id` 即可。

### Q: 如何清空对话历史？
A: 
- Web 界面：点击"🗑️ 清空对话"或"🔄 新建会话"
- API：`DELETE /api/v1/history/{session_id}`

### Q: 策略选择逻辑在哪里配置？
A: 策略选择逻辑在 `llm_agents.py` 的 `StrategySelectionAgent` 中，通过 system prompt 配置选择原则。也可以查看 `strategies/STRATEGY_GUIDE.md` 了解完整的决策树。

---

## 📄 License

MIT License

---

**💙 情感陪伴助手 - 用 AI 传递温暖**