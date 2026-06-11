"""用户表 ORM 模型"""
from sqlalchemy import Column, Integer, String

from ..database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
