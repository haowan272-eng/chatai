"""认证路由：登录、注册、刷新 token"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, TokenResponse, RefreshRequest
from ..auth import create_access_token, create_refresh_token
from ..config import REFRESH_SECRET_KEY, ALGORITHM

import jwt

router = APIRouter(tags=["认证"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """登录 — 验证用户名密码，返回 access_token + refresh_token"""
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在，请注册")
    if user.password != req.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密码错误")
    return TokenResponse(
        access_token=create_access_token(req.username),
        refresh_token=create_refresh_token(req.username),
    )


@router.post("/register")
def register(req: LoginRequest, db: Session = Depends(get_db)):
    """注册 — 创建新用户"""
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    user = User(username=req.username, password=req.password)
    db.add(user)
    db.commit()
    return {"message": "注册成功", "username": req.username}


@router.post("/refresh", response_model=TokenResponse)
def refresh(req: RefreshRequest):
    """刷新 token — 用 refresh_token 换新的 access_token"""
    try:
        payload = jwt.decode(req.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload["sub"]
        return TokenResponse(
            access_token=create_access_token(username),
            refresh_token=create_refresh_token(username),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
