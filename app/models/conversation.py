"""会话表 ORM 模型"""
from sqlalchemy import Column, Integer, String, ForeignKey

from ..database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    title = Column(String, default="新会话")
    user_id = Column(Integer, ForeignKey("users.id"))
