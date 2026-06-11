"""聊天相关的 Pydantic 请求/响应模型"""
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """聊天请求体"""
    message: str
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    """聊天响应体"""
    answer: str
    conversation_id: int
