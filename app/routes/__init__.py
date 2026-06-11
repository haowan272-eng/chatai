"""路由聚合 — 所有子路由在此注册"""
from fastapi import APIRouter

from .auth import router as auth_router
from .chat import router as chat_router
from .user import router as user_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(user_router)
