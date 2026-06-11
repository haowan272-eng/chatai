"""DeepSeek LLM 客户端与调用函数"""
from openai import AsyncOpenAI

from ..config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, SYSTEM_PROMPT

# 异步客户端 — FastAPI 异步路由里直接 await，不阻塞事件循环
llm_client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)

# 启动时检查 API Key 是否已配置
if DEEPSEEK_API_KEY == "sk-your-deepseek-api-key":
    print("[WARNING] DeepSeek API Key not set! Set env DEEPSEEK_API_KEY or edit app/config.py")


async def call_deepseek(messages: list[dict]) -> str:
    """
    调用 DeepSeek LLM，返回 AI 回复文本。
    messages 格式: [{"role": "system"|"user"|"assistant", "content": "..."}, ...]
    """
    try:
        response = await llm_client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"DeepSeek API error: {e}")
        return f"抱歉，AI 服务暂时不可用，请稍后重试。错误: {str(e)}"


async def call_deepseek_stream(messages: list[dict]):
    """
    流式调用 DeepSeek LLM，逐 token yield 返回。
    用法: async for token in call_deepseek_stream(messages): ...
    """
    try:
        stream = await llm_client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
    except Exception as e:
        print(f"DeepSeek stream error: {e}")
        yield f"\n[抱歉，AI 服务暂时不可用。错误: {str(e)}]"
