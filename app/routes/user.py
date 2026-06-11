"""用户路由：个人信息、会话列表"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Conversation
from ..dependencies import get_current_user

router = APIRouter(tags=["用户"])


@router.get("/profile")
def profile(current_user: str = Depends(get_current_user)):
    """获取当前用户信息（需登录）"""
    return {"username": current_user, "status": "active"}


@router.get("/conversations")
def list_conversations(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查看当前用户的所有会话（需登录）"""
    user = db.query(User).filter(User.username == current_user).first()
    convs = db.query(Conversation).filter(Conversation.user_id == user.id).all()
    return [{"id": c.id, "title": c.title} for c in convs]
