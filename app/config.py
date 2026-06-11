"""
集中管理所有配置常量 — 从 .env 文件加载，环境变量优先
"""
import os
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
load_dotenv()

# ==================== 数据库配置 ====================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://18034:postgres@localhost:5432/postgres",
)

# ==================== JWT 配置 ====================
SECRET_KEY = os.getenv("SECRET_KEY", "123456")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "my-refresh-secret-key")
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "1440"))

# ==================== DeepSeek LLM 配置 ====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-your-deepseek-api-key")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "你是一个有帮助的AI助手。请用中文回答用户的问题，语气友好、简洁。"
    "如果用户问技术问题，尽量提供代码示例。",
)

# ==================== 服务器配置 ====================
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
