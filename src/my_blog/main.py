"""My Blog API 入口"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import create_db_and_tables
from .api.v1 import auth, users, posts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时创建数据库和表
    create_db_and_tables()
    yield
    # 关闭时清理资源（如果需要）


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to My Blog API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
