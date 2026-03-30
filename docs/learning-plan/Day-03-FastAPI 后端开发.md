# Day 03 - FastAPI 后端开发

> 目标：掌握现代 Python Web 框架，构建生产级 RESTful API

---

## 📋 今日学习目标

- [ ] 理解 FastAPI 的核心概念与优势
- [ ] 掌握 Pydantic 数据验证
- [ ] 实现路由、依赖注入、中间件
- [ ] 掌握异步编程 async/await
- [ ] 集成数据库（SQLModel）
- [ ] 实现认证与授权

---

## 🚀 第一部分：FastAPI 简介（30 分钟）

### 1.1 为什么选择 FastAPI

| 特性 | FastAPI | Flask | Django | Spring Boot |
|------|---------|-------|--------|-------------|
| **异步支持** | ✅ 原生 | ❌ 需扩展 | ✅ 3.0+ | ✅ |
| **自动文档** | ✅ OpenAPI | ❌ | ❌ | ✅ |
| **类型检查** | ✅ Pydantic | ❌ | ❌ | ✅ |
| **性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **学习曲线** | 低 | 低 | 中 | 高 |

**核心优势**：
- 基于 Starlette（ASGI 框架）
- 基于 Pydantic（数据验证）
- 自动生成 OpenAPI/Swagger 文档
- 原生异步支持

### 1.2 第一个 FastAPI 应用

```python
"""src/python_mastery/main.py"""
from fastapi import FastAPI

app = FastAPI(
    title="Python Mastery API",
    description="7 天精通 Python 学习计划示例 API",
    version="0.1.0",
)


@app.get("/")
async def root():
    """根路径"""
    return {"message": "Hello, World!", "status": "ok"}


@app.get("/items/{item_id}")
async def get_item(item_id: int, show_details: bool = False):
    """获取物品信息"""
    return {
        "item_id": item_id,
        "show_details": show_details,
        "name": f"Item {item_id}",
    }


# 运行：uv run uvicorn src.python_mastery.main:app --reload
# 访问：http://localhost:8000/docs (Swagger UI)
#       http://localhost:8000/redoc (ReDoc)
```

### 1.3 项目结构

```
python-mastery/
├── pyproject.toml
├── src/
│   └── python_mastery/
│       ├── __init__.py
│       ├── main.py              # 应用入口
│       ├── config.py            # 配置管理
│       ├── api/
│       │   ├── __init__.py
│       │   ├── v1/
│       │   │   ├── __init__.py
│       │   │   ├── users.py     # 用户路由
│       │   │   └── items.py     # 物品路由
│       │   └── deps.py          # 依赖注入
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py          # 用户模型
│       │   └── item.py          # 物品模型
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── user.py          # 用户 Schema
│       │   └── item.py          # 物品 Schema
│       └── services/
│           ├── __init__.py
│           └── user_service.py  # 业务逻辑
└── tests/
    ├── __init__.py
    ├── conftest.py              # pytest 配置
    └── test_api/
        ├── test_users.py
        └── test_items.py
```

---

## 📦 第二部分：Pydantic 数据验证（1 小时）

### 2.1 基础 Schema

```python
"""src/python_mastery/schemas/user.py"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator


class UserBase(BaseModel):
    """用户基础 Schema"""
    email: EmailStr = Field(..., description="用户邮箱", example="user@example.com")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(..., min_length=8, description="密码")

    @validator("password")
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """更新用户请求（所有字段可选）"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True  # 允许从 ORM 对象读取数据


class UserInDB(UserResponse):
    """数据库中的用户（包含敏感字段）"""
    hashed_password: str
```

### 2.2 嵌套 Schema

```python
"""src/python_mastery/schemas/item.py"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .user import UserResponse


class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0, description="价格必须大于 0")
    tax: Optional[float] = Field(None, ge=0)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: Optional[float] = None


class ItemResponse(ItemBase):
    id: int
    owner_id: int
    owner: Optional[UserResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True
```

### 2.3 响应模型

```python
"""在路由中使用"""
from fastapi import FastAPI, status
from .schemas.user import UserCreate, UserResponse

app = FastAPI()


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """创建用户"""
    # Pydantic 会自动验证请求体
    return {
        "id": 1,
        "email": user.email,
        "username": user.username,
        "is_active": True,
        "created_at": datetime.now(),
    }
```

---

## 🛣️ 第三部分：路由与 API 设计（1 小时）

### 3.1 APIRouter 组织路由

```python
"""src/python_mastery/api/v1/users.py"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...api.deps import get_db
from ...schemas.user import UserCreate, UserResponse, UserUpdate
from ...services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """获取用户列表"""
    return UserService.get_users(db, skip=skip, limit=limit)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """创建新用户"""
    # 检查邮箱是否已存在
    existing = UserService.get_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return UserService.create(db, user_in=user_in)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """获取单个用户"""
    user = UserService.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
):
    """更新用户"""
    user = UserService.update(db, user_id=user_id, user_in=user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """删除用户"""
    if not UserService.delete(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
```

### 3.2 主应用注册路由

```python
"""src/python_mastery/main.py"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import users, items

app = FastAPI(
    title="Python Mastery API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 前端
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
```

### 3.3 HTTP 状态码规范

```python
from fastapi import status

# 2xx 成功
status.HTTP_200_OK           # GET, PUT, PATCH 成功
status.HTTP_201_CREATED      # POST 创建成功
status.HTTP_204_NO_CONTENT   # DELETE 成功

# 4xx 客户端错误
status.HTTP_400_BAD_REQUEST  # 请求参数错误
status.HTTP_401_UNAUTHORIZED # 未认证
status.HTTP_403_FORBIDDEN    # 无权限
status.HTTP_404_NOT_FOUND    # 资源不存在
status.HTTP_409_CONFLICT     # 资源冲突（如重复）

# 5xx 服务端错误
status.HTTP_500_INTERNAL_SERVER_ERROR
```

---

## 🔄 第四部分：异步编程（30 分钟）

### 4.1 async/await 基础

```python
import asyncio
import aiohttp
from fastapi import FastAPI

app = FastAPI()


# 同步函数（阻塞）
def fetch_data_sync(url: str) -> dict:
    import requests
    return requests.get(url).json()


# 异步函数（非阻塞）
async def fetch_data_async(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


# FastAPI 异步端点
@app.get("/data")
async def get_data():
    # 多个并发请求
    urls = ["http://api1.com", "http://api2.com", "http://api3.com"]
    results = await asyncio.gather(*[fetch_data_async(url) for url in urls])
    return {"results": results}


# 后台任务
async def send_email(email: str):
    # 模拟发送邮件
    await asyncio.sleep(1)
    print(f"Email sent to {email}")


@app.post("/register")
async def register(email: str):
    # 注册后异步发送邮件（不阻塞响应）
    asyncio.create_task(send_email(email))
    return {"status": "registered"}
```

### 4.2 异步数据库操作

```python
"""使用异步数据库驱动"""
import databases
from sqlalchemy import create_engine, MetaData

# 异步数据库
database = databases.Database("postgresql+asyncpg://user:pass@localhost/dbname")

# 同步数据库（用于迁移）
engine = create_engine("postgresql://user:pass@localhost/dbname")
metadata = MetaData()


# FastAPI 生命周期事件
@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# 在路由中使用
@app.get("/users")
async def get_users():
    query = "SELECT * FROM users"
    return await database.fetch_all(query)
```

---

## 🗄️ 第五部分：SQLModel 数据库集成（1 小时）

### 5.1 定义模型

```python
"""src/python_mastery/models/user.py"""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    """用户数据库模型"""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(min_length=3, max_length=50)
    hashed_password: str
    full_name: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    items: list["Item"] = Relationship(back_populates="owner")


class UserCreate(SQLModel):
    """创建用户请求"""
    email: str
    username: str
    password: str
    full_name: Optional[str] = None


class UserRead(SQLModel):
    """用户响应"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
```

### 5.2 数据库会话管理

```python
"""src/python_mastery/api/deps.py"""
from collections.abc import Generator
from sqlmodel import Session, create_engine
from fastapi import Depends

from ..config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL 日志
    pool_pre_ping=True,   # 连接健康检查
    pool_size=10,
    max_overflow=20,
)


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话（依赖注入）"""
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
```

### 5.3 CRUD 操作

```python
"""src/python_mastery/services/user_service.py"""
from sqlmodel import Session, select
from passlib.context import CryptContext
from typing import List, Optional

from ..models.user import User, UserCreate, UserUpdate, UserRead

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    def get(db: Session, user_id: int) -> Optional[User]:
        return db.get(User, user_id)

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return db.exec(statement).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        statement = select(User).offset(skip).limit(limit)
        return db.exec(statement).all()

    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        user = User.from_orm(user_in)
        user.hashed_password = pwd_context.hash(user_in.password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user_id: int, user_in: UserUpdate) -> Optional[User]:
        user = db.get(User, user_id)
        if not user:
            return None

        update_data = user_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        user = db.get(User, user_id)
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True
```

### 5.4 数据库迁移（Alembic）

```bash
# 安装 Alembic
uv add alembic

# 初始化
uv run alembic init alembic

# 配置 alembic.ini
# sqlalchemy.url = postgresql://user:pass@localhost/dbname

# 配置 alembic/env.py
# 从 SQLModel 导入元数据
from sqlmodel import SQLModel
target_metadata = SQLModel.metadata

# 创建迁移
uv run alembic revision --autogenerate -m "Initial migration"

# 应用迁移
uv run alembic upgrade head

# 回滚
uv run alembic downgrade -1
```

---

## 🔐 第六部分：认证与授权（1 小时）

### 6.1 JWT 认证实现

```python
"""src/python_mastery/security.py"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from .api.deps import get_db
from .models.user import User

# 配置
SECRET_KEY = "your-secret-key"  # 生产环境使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = verify_token(token)
    if user_id is None:
        raise credentials_exception

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user
```

### 6.2 认证路由

```python
"""src/python_mastery/api/v1/auth.py"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from datetime import timedelta

from ...api.deps import get_db
from ...models.user import User, UserCreate
from ...security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context
from ...services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=dict)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """注册新用户"""
    # 检查邮箱
    if UserService.get_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 创建用户
    user = UserService.create(db, user_in)
    return {"message": "User created successfully", "user_id": user.id}


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """登录获取 access token"""
    user = UserService.get_by_email(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "token_type": "bearer"}
```

### 6.3 受保护的路由

```python
from fastapi import Depends
from .deps import get_current_user
from .models.user import User


@app.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """获取当前用户信息"""
    return current_user


@app.post("/admin/users", response_model=UserRead)
async def create_user_as_admin(
    user_in: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """管理员创建用户（需要超级用户权限）"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return UserService.create(db, user_in)
```

---

## 💻 第七部分：实战练习（1 小时）

### 任务：完整的 Blog API

实现以下功能：

```python
"""
Blog API 需求

1. 用户系统
   - POST /api/v1/auth/register - 注册
   - POST /api/v1/auth/login - 登录
   - GET /api/v1/users/me - 获取当前用户

2. 文章管理（需要认证）
   - GET /api/v1/posts - 获取所有文章（公开）
   - GET /api/v1/posts/{id} - 获取单篇文章（公开）
   - POST /api/v1/posts - 创建文章（需认证）
   - PUT /api/v1/posts/{id} - 更新文章（仅作者）
   - DELETE /api/v1/posts/{id} - 删除文章（仅作者）

3. 评论系统
   - GET /api/v1/posts/{id}/comments - 获取评论
   - POST /api/v1/posts/{id}/comments - 添加评论（需认证）
"""
```

### 项目结构

```
src/python_mastery/
├── main.py
├── config.py
├── security.py
├── api/
│   ├── deps.py
│   └── v1/
│       ├── auth.py
│       ├── users.py
│       ├── posts.py
│       └── comments.py
├── models/
│   ├── user.py
│   ├── post.py
│   └── comment.py
├── schemas/
│   ├── user.py
│   ├── post.py
│   └── comment.py
└── services/
    ├── user_service.py
    ├── post_service.py
    └── comment_service.py
```

---

## ✅ 第八部分：今日检查清单

### API 检查

```bash
# 启动服务
uv run uvicorn src.python_mastery.main:app --reload

# 测试端点
curl http://localhost:8000/health

# 访问文档
open http://localhost:8000/docs
```

### 测试

```bash
# 运行 API 测试
uv run pytest tests/test_api/ -v

# 带覆盖率
uv run pytest --cov=src/python_mastery
```

### 知识检查

- [ ] 理解 FastAPI 的路由机制
- [ ] 掌握 Pydantic 数据验证
- [ ] 理解依赖注入的工作原理
- [ ] 能实现 JWT 认证
- [ ] 掌握 SQLModel CRUD 操作
- [ ] 理解 async/await 的使用场景

---

## 🚀 明日预告

**Day 04 - LangChain Agent 开发基础**

- LangChain 核心概念
- Prompt Template 与 LCEL
- Chain 与 Memory
- 向量数据库集成

---

## 📝 参考资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLModel 文档](https://sqlmodel.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [Awesome FastAPI](https://github.com/mjhea0/awesome-fastapi)
