"""FastAPI 应用入口 — 创建 app、启动事件、路由注册"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base, SessionLocal
from .models import User
from .routes import api_router

app = FastAPI(title="AI Chat API with DeepSeek")

# CORS — 允许前端页面跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
def on_startup():
    """启动时：建表 + 种子用户"""
    # 建表（已存在的表不会重复创建）
    Base.metadata.create_all(bind=engine)

    # 种子用户：首次启动自动创建 admin/123456
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(username="admin", password="123456"))
            db.commit()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database init failed (PostgreSQL may be down): {e}")
    finally:
        db.close()
