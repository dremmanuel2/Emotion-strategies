"""
智能体系统测试脚本
"""
import asyncio
import httpx
from typing import Optional


async def test_agent_analyze(
    text: str,
    base_url: str = "http://100.100.30.150",
    api_key: Optional[str] = None
):
    """测试智能体分析接口"""
    print(f"\n{'='*60}")
    print(f"测试：智能体分析")
    print(f"输入：{text}")
    print(f"{'='*60}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        params = {"text": text}
        if api_key:
            params["api_key"] = api_key
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/agent/analyze",
                params=params
            )
            result = response.json()
            
            print(f"\n分析结果:")
            print(f"  情绪：{result.get('emotion', {}).get('type', 'N/A')}")
            print(f"  状态:")
            print(f"    - 阶段：{result.get('state', {}).get('stage', 'N/A')}")
            print(f"    - 强度：{result.get('state', {}).get('intensity', 'N/A')}")
            print(f"    - 风险：{result.get('state', {}).get('risk', 'N/A')}")
            print(f"  策略：{result.get('selected_strategy', 'N/A')}")
            print(f"  成功：{result.get('success', False)}")
            
            return result
        except Exception as e:
            print(f"❌ 测试失败：{e}")
            return None


async def test_agent_full_respond(
    text: str,
    base_url: str = "http://100.100.30.150",
    api_key: Optional[str] = None
):
    """测试智能体完整响应接口"""
    print(f"\n{'='*60}")
    print(f"测试：智能体完整响应")
    print(f"输入：{text}")
    print(f"{'='*60}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        params = {"text": text}
        if api_key:
            params["api_key"] = api_key
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/agent/full_respond",
                params=params
            )
            result = response.json()
            
            print(f"\n完整响应:")
            print(f"  情绪：{result.get('emotion', 'N/A')}")
            print(f"  状态:")
            print(f"    - 阶段：{result.get('state', {}).get('stage', 'N/A')}")
            print(f"    - 强度：{result.get('state', {}).get('intensity', 'N/A')}")
            print(f"    - 风险：{result.get('state', {}).get('risk', 'N/A')}")
            print(f"  策略：{result.get('strategy', 'N/A')}")
            print(f"\n  回复:")
            print(f"    {result.get('response_text', 'N/A')}")
            
            if result.get('methods'):
                print(f"\n  执行方法:")
                for method in result['methods']:
                    print(f"    - {method['method_name']}: {method['content'][:50]}...")
            
            print(f"\n  成功：{result.get('success', False)}")
            
            return result
        except Exception as e:
            print(f"❌ 测试失败：{e}")
            return None


async def test_emotion_respond_with_agent(
    text: str,
    emotion: str = "neutral",
    base_url: str = "http://100.100.30.150",
    use_agent: bool = True
):
    """测试原有接口（使用智能体）"""
    print(f"\n{'='*60}")
    print(f"测试：原有接口 (use_agent={use_agent})")
    print(f"输入：{text} | 情绪：{emotion}")
    print(f"{'='*60}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "text": text,
            "emotion": emotion
        }
        
        try:
            response = await client.post(
                f"{base_url}/api/v1/emotion/respond",
                params={"use_agent": use_agent},
                json=payload
            )
            result = response.json()
            
            print(f"\n响应:")
            print(f"  策略：{result.get('strategy', 'N/A')}")
            print(f"  回复：{result.get('response_text', 'N/A')[:100]}...")
            
            if result.get('methods'):
                print(f"\n  执行方法:")
                for method in result['methods']:
                    print(f"    - {method['method_name']}")
            
            return result
        except Exception as e:
            print(f"❌ 测试失败：{e}")
            return None


async def run_all_tests(base_url: str = "http://100.100.30.150", api_key: Optional[str] = None):
    """运行所有测试"""
    print("\n" + "="*60)
    print("智能体系统测试套件")
    print("="*60)
    
    # 测试用例
    test_cases = [
        {
            "text": "我今天心情特别不好，感觉做什么都没意义",
            "emotion": "sad",
            "description": "悲伤情绪 - 有风险信号"
        },
        {
            "text": "气死我了！那个人怎么能这样对我！",
            "emotion": "angry",
            "description": "愤怒情绪 - 发泄状态"
        },
        {
            "text": "最近总是睡不着，很担心自己的身体状况",
            "emotion": "anxious",
            "description": "焦虑情绪 - 求助状态"
        },
        {
            "text": "今天中了个小奖，好开心！",
            "emotion": "positive",
            "description": "积极情绪 - 分享喜悦"
        },
        {
            "text": "今天天气不错，出去散了个步",
            "emotion": "neutral",
            "description": "中性情绪 - 日常交流"
        },
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n\n{'#'*60}")
        print(f"# 测试用例 {i}: {case['description']}")
        print(f"{'#'*60}")
        
        # 测试智能体完整响应
        await test_agent_full_respond(case["text"], base_url, api_key)
        
        # 测试原有接口（使用智能体）
        await test_emotion_respond_with_agent(
            case["text"],
            case["emotion"],
            base_url,
            use_agent=True
        )
    
    print("\n\n" + "="*60)
    print("所有测试完成")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    base_url = "http://100.100.30.150"
    api_key = None
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    if len(sys.argv) > 2:
        api_key = sys.argv[2]
    
    asyncio.run(run_all_tests(base_url, api_key))