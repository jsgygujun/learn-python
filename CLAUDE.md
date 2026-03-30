# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run tests
uv run pytest

# Run single test file
uv run pytest tests/test_<name>.py -v

# Run Blog API tests
uv run pytest tests/test_api/ -v

# Run tests with coverage
uv run pytest --cov=src

# Lint check
uv run ruff check .

# Format code
uv run ruff format .

# Type check
uv run pyright .

# Run main script
uv run python main.py

# Run Blog API (development server)
uv run uvicorn src.my_blog.main:app --reload
```

## Architecture

项目包含两个独立的子项目：

### 1. `src/python_mastery/` - Python 学习示例
- **`data_tools.py`** - 数据处理工具函数
- **`tests/test_data_tools.py`** - 对应测试

### 2. `src/my_blog/` - My Blog API
- **`main.py`** - FastAPI 应用入口
- **`config.py`** - 应用配置（使用 pydantic-settings）
- **`database.py`** - 数据库连接（AsyncSession）
- **`security.py`** - JWT 认证和密码加密
- **`models/`** - SQLModel 数据库模型
  - `user.py` - 用户模型
  - `post.py` - 文章模型
  - `comment.py` - 评论模型
- **`schemas/`** - Pydantic Schema（请求/响应）
- **`services/`** - 业务逻辑层
- **`api/`** - API 路由层
  - `deps.py` - 依赖注入
  - `v1/` - API v1 版本路由

### 3. `tests/` - 测试代码目录
- **`conftest.py`** - pytest 配置和 fixtures
- **`test_api/`** - Blog API 测试

### 4. `docs/learning-plan/` - 学习计划文档（Day-01 ~ Day-07）

项目采用标准的 Python 包结构，源代码位于 `src/` 下，测试位于 `tests/` 下。pytest 配置已设置 `pythonpath = ["src"]`，测试中直接使用 `from src.my_blog.xxx import yyy` 导入。

## My Blog API 架构细节

### 认证流程
1. 用户注册/登录 → `/api/v1/auth/register` 或 `/api/v1/auth/login`
2. 服务端验证后返回 JWT token
3. 客户端在请求头携带 `Authorization: Bearer <token>`
4. 服务端通过 `get_current_user` 依赖注入验证 token

### 数据库
- 使用 SQLModel（SQLAlchemy + Pydantic）
- 异步会话：`AsyncSession`
- 默认 SQLite（可切换到 PostgreSQL/MySQL）

### 服务层模式
- `UserService` - 用户 CRUD
- `PostService` - 文章 CRUD
- `CommentService` - 评论 CRUD

## Tool Configuration

所有工具配置均在 `pyproject.toml` 中：

| 工具 | 用途 |
|------|------|
| **uv** | 包管理 + 虚拟环境 |
| **ruff** | Lint + Format（规则：E/F/I/N/W/UP/B） |
| **pyright** | 类型检查（strict 模式） |
| **pytest** | 测试框架（asyncio_mode = auto） |

Python 版本：3.12+

## Security Notes

- `SECRET_KEY` 必须从环境变量读取，不要硬编码
- 生产环境配置 `ALLOWED_ORIGINS` 限制具体域名
- 密码最小长度 8 位
