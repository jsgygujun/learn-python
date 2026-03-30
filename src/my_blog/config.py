"""应用配置"""

import secrets
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


def generate_secret_key() -> str:
    """生成安全的随机密钥"""
    return secrets.token_urlsafe(32)


# 如果环境变量未设置 SECRET_KEY，则生成临时密钥（仅开发环境）
_secret_key = os.getenv("SECRET_KEY") or generate_secret_key()


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 应用配置
    APP_NAME: str = "My Blog API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./blog.db"

    # JWT 配置 - SECRET_KEY 从环境变量读取或自动生成（开发环境）
    SECRET_KEY: str = _secret_key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS 配置
    ALLOWED_ORIGINS: str = "*"  # 逗号分隔的域名列表

    @property
    def allowed_origins_list(self) -> list[str]:
        """解析允许的域名列表"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
