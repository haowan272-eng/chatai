"""认证相关的 Pydantic 请求/响应模型"""
from pydantic import BaseModel


class LoginRequest(BaseModel):
    """登录请求体"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """登录成功返回"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """刷新 token 请求体"""
    refresh_token: str
