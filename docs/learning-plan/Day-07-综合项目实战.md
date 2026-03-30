# Day 07 - 综合项目实战

> 目标：整合一周所学，构建完整的生产级 AI Agent 应用

---

## 📋 今日学习目标

- [ ] 设计完整的项目架构
- [ ] 实现 AI Agent 应用
- [ ] 编写测试与文档
- [ ] 配置 CI/CD 与部署

---

## 🏗️ 第一部分：项目架构设计（1 小时）

### 1.1 项目需求

**项目名称**：智能研究助手（Research Agent）

**功能需求**：
1. 用户认证系统（注册/登录/JWT）
2. 研究任务管理（创建/列表/删除）
3. AI Agent 执行研究任务
4. 实时查看研究进度
5. 生成并下载报告

**技术栈**：
- 后端：FastAPI + SQLModel
- Agent：LangChain + LangGraph
- 前端：HTMX（快速）或 React（完整）
- 数据库：PostgreSQL + Chroma
- 任务队列：Celery + Redis（可选）

### 1.2 项目结构

```
research-agent/
├── pyproject.toml
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
│
├── src/
│   └── research_agent/
│       ├── __init__.py
│       ├── main.py              # FastAPI 入口
│       ├── config.py            # 配置管理
│       ├── database.py          # 数据库连接
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── deps.py          # 依赖注入
│       │   ├── v1/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py      # 认证路由
│       │   │   ├── tasks.py     # 任务路由
│       │   │   └── research.py  # 研究路由
│       │   └── websocket.py     # WebSocket 通知
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── task.py
│       │   └── research_result.py
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── task.py
│       │   └── research.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── auth_service.py
│       │   ├── task_service.py
│       │   └── research_service.py
│       │
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── tools.py         # Agent 工具
│       │   ├── graph.py         # LangGraph 定义
│       │   └── planner.py       # 任务规划
│       │
│       └── templates/
│           ├── base.html
│           ├── index.html
│           └── components/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_agents/
│   └── test_services/
│
└── scripts/
    ├── dev.sh                   # 开发脚本
    ├── prod.sh                  # 生产脚本
    └── migrate.py               # 数据库迁移
```

---

## 🔧 第二部分：核心实现（3 小时）

### 2.1 配置文件

```python
"""src/research_agent/config.py"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用
    APP_NAME: str = "Research Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "postgresql://user:pass@localhost/research"

    # Redis（任务队列）
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # LLM
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    TEMPERATURE: float = 0.7

    # 向量数据库
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # 限流
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
```

### 2.2 数据模型

```python
"""src/research_agent/models/task.py"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(SQLModel, table=True):
    """研究任务"""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200, index=True)
    description: str = Field(max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    progress: int = Field(default=0, ge=0, le=100)  # 0-100

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # 关系
    user_id: int = Field(foreign_key="users.id")
    user: "User" = Relationship(back_populates="tasks")
    results: list["ResearchResult"] = Relationship(back_populates="task")

    # 结果
    summary: Optional[str] = Field(default=None, max_length=5000)
    error_message: Optional[str] = None


class ResearchResult(SQLModel, table=True):
    """研究结果"""

    __tablename__ = "research_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id")
    task: "Task" = Relationship(back_populates="results")

    content: str = Field(max_length=50000)
    source_url: Optional[str] = Field(max_length=500)
    relevance_score: float = Field(default=0.0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2.3 Agent 实现

```python
"""src/research_agent/agents/tools.py"""
from langchain_core.tools import tool
from typing import List
import aiohttp
from datetime import datetime


@tool
def search_academic(query: str, year_from: int = 2020) -> str:
    """搜索学术论文。

    Args:
        query: 搜索关键词
        year_from: 起始年份

    Returns:
        论文摘要列表
    """
    # 实际使用 Semantic Scholar API 或 arXiv API
    return f"搜索到 {query} 相关的学术论文..."


@tool
def search_web(query: str, num_results: int = 10) -> str:
    """搜索互联网获取信息。

    Args:
        query: 搜索关键词
        num_results: 返回结果数量

    Returns:
        搜索结果摘要
    """
    from tavily import TavilyClient
    import os

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search(query, max_results=num_results)

    results = []
    for r in response["results"]:
        results.append(f"标题：{r['title']}\n内容：{r['content']}\nURL: {r['url']}")

    return "\n\n".join(results)


@tool
def summarize_text(text: str, max_length: int = 500) -> str:
    """总结长文本。

    Args:
        text: 要总结的文本
        max_length: 最大长度

    Returns:
        总结结果
    """
    # 调用 LLM 进行总结
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    from langchain_core.prompts import ChatPromptTemplate

    prompt = ChatPromptTemplate.from_messages([
        ("system", "请用简洁的语言总结以下内容，不超过{max_length}字。"),
        ("human", "{text}"),
    ])

    chain = prompt | llm
    response = chain.invoke({"max_length": max_length, "text": text})

    return response.content


@tool
def save_research_report(title: str, content: str, format: str = "md") -> str:
    """保存研究报告。

    Args:
        title: 报告标题
        content: 报告内容
        format: 文件格式（md/pdf/txt）

    Returns:
        保存路径
    """
    from pathlib import Path

    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title[:50]}_{timestamp}.{format}"
    filepath = output_dir / filename

    filepath.write_text(content, encoding="utf-8")

    return f"报告已保存：{filepath}"


def get_research_tools():
    """获取所有研究工具"""
    return [search_academic, search_web, summarize_text, save_research_report]
```

### 2.4 LangGraph Agent

```python
"""src/research_agent/agents/graph.py"""
from typing import TypedDict, Annotated, List, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .tools import get_research_tools


class ResearchState(TypedDict):
    """研究状态"""
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    task_id: int
    current_step: int
    total_steps: int
    collected_data: List[dict]
    progress: int


class ResearchAgent:
    """研究 Agent"""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        tools = get_research_tools()
        self.llm_with_tools = self.llm.bind_tools(tools)
        self.tools = tools

    def should_continue(self, state: ResearchState) -> Literal["tools", "synthesize"]:
        """判断是否继续调用工具"""
        messages = state["messages"]
        last_message = messages[-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "synthesize"

    def plan(self, state: ResearchState) -> ResearchState:
        """规划研究步骤"""
        # 分析任务，制定计划
        messages = state["messages"]

        system_prompt = """你是一个研究助手。请分析用户的研究需求，制定研究计划。

研究计划应该包括：
1. 确定研究问题和关键词
2. 搜索相关信息
3. 整理和分析数据
4. 生成研究报告

请开始规划。"""

        plan_messages = [HumanMessage(content=system_prompt)] + messages
        response = self.llm.invoke(plan_messages)

        return {
            "messages": [response],
            "current_step": 1,
        }

    def execute_search(self, state: ResearchState) -> ResearchState:
        """执行搜索"""
        # 提取搜索关键词并调用工具
        messages = state["messages"]

        search_prompt = "请根据研究问题，生成合适的搜索关键词，并调用搜索工具。"
        search_messages = [HumanMessage(content=search_prompt)] + messages

        response = self.llm_with_tools.invoke(search_messages)

        return {
            "messages": [response],
            "progress": state["progress"] + 25,
        }

    def synthesize(self, state: ResearchState) -> ResearchState:
        """综合研究结果"""
        messages = state["messages"]

        synthesis_prompt = """请综合以上所有信息和研究结果，生成一份完整的研究报
告。

报告应该包括：
1. 研究背景和目标
2. 主要发现
3. 关键结论
4. 参考文献

请用中文撰写报告。"""

        synthesis_messages = [HumanMessage(content=synthesis_prompt)] + messages
        response = self.llm.invoke(synthesis_messages)

        return {
            "messages": [response],
            "progress": 100,
        }

    def create_graph(self):
        """创建研究图"""
        workflow = StateGraph(ResearchState)

        # 添加节点
        workflow.add_node("plan", self.plan)
        workflow.add_node("search", self.execute_search)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.add_node("synthesize", self.synthesize)

        # 设置流程
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "search")
        workflow.add_conditional_edges(
            "search",
            self.should_continue,
            {
                "tools": "tools",
                "synthesize": "synthesize",
            }
        )
        workflow.add_edge("tools", "search")
        workflow.add_edge("synthesize", END)

        return workflow.compile()
```

### 2.5 API 路由

```python
"""src/research_agent/api/v1/tasks.py"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from ...api.deps import get_db, get_current_user
from ...models.user import User
from ...models.task import Task, TaskStatus
from ...schemas.task import TaskCreate, TaskResponse, TaskUpdate
from ...services.task_service import TaskService
from ...services.research_service import ResearchService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status_filter: TaskStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取用户的研究任务列表"""
    return TaskService.get_user_tasks(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
    )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建新的研究任务"""
    # 创建任务
    task = TaskService.create(db, task_in=task_in, user_id=current_user.id)

    # 在后台执行研究
    background_tasks.add_task(
        ResearchService.run_research,
        task_id=task.id,
    )

    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取任务详情"""
    task = TaskService.get(db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )
    return task


@router.post("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """取消任务"""
    task = TaskService.cancel(db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除任务"""
    if not TaskService.delete(db, task_id=task_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )
```

### 2.6 研究服务

```python
"""src/research_agent/services/research_service.py"""
from sqlmodel import Session, select
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from datetime import datetime

from ..models.task import Task, TaskStatus, ResearchResult
from ..agents.graph import ResearchAgent


class ResearchService:
    """研究服务"""

    @staticmethod
    async def run_research(session: Session, task_id: int):
        """执行研究任务"""
        # 更新任务状态
        task = session.get(Task, task_id)
        if not task:
            return

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        session.add(task)
        session.commit()

        try:
            # 初始化 Agent
            agent = ResearchAgent()
            graph = agent.create_graph()

            # 准备初始消息
            initial_message = HumanMessage(
                content=f"请研究以下主题：{task.title}\n\n详细描述：{task.description}"
            )

            # 运行研究
            initial_state = {
                "messages": [initial_message],
                "task_id": task_id,
                "current_step": 0,
                "total_steps": 4,
                "collected_data": [],
                "progress": 0,
            }

            # 流式执行
            final_state = None
            for event in graph.stream(initial_state):
                # 更新进度
                if "progress" in event.get("synthesize", {}):
                    progress = event["synthesize"]["progress"]
                    task.progress = progress
                    session.add(task)
                    session.commit()

                final_state = event

            # 保存结果
            if final_state and "synthesize" in final_state:
                result_message = final_state["synthesize"]["messages"][-1]

                result = ResearchResult(
                    task_id=task_id,
                    content=result_message.content,
                )
                session.add(result)

                # 完成任务
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.summary = result.content[:500]  # 前 500 字作为摘要
                session.add(task)
                session.commit()

        except Exception as e:
            # 任务失败
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            session.add(task)
            session.commit()
            raise
```

### 2.7 前端页面（HTMX）

```html
<!-- src/research_agent/templates/index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Agent</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <header class="mb-8">
            <h1 class="text-4xl font-bold text-gray-800">🔬 Research Agent</h1>
            <p class="text-gray-600 mt-2">智能研究助手，帮你快速收集和分析信息</p>
        </header>

        <!-- 创建任务 -->
        <div class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-xl font-bold mb-4">创建新研究</h2>
            <form
                hx-post="/api/v1/tasks"
                hx-target="#tasks-list"
                hx-swap="beforeend"
                class="space-y-4">

                <div>
                    <label class="block text-sm font-medium text-gray-700">研究主题</label>
                    <input
                        type="text"
                        name="title"
                        placeholder="例如：2024 年 AI 发展趋势"
                        class="mt-1 block w-full border border-gray-300 rounded-md px-4 py-2"
                        required />
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700">详细描述</label>
                    <textarea
                        name="description"
                        rows="4"
                        placeholder="请详细描述你的研究需求..."
                        class="mt-1 block w-full border border-gray-300 rounded-md px-4 py-2"></textarea>
                </div>

                <button
                    type="submit"
                    class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded">
                    开始研究
                </button>
            </form>
        </div>

        <!-- 任务列表 -->
        <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-bold mb-4">我的研究</h2>
            <div id="tasks-list" hx-get="/api/v1/tasks" hx-trigger="load every 5s">
                <!-- 动态加载任务列表 -->
            </div>
        </div>
    </div>
</body>
</html>
```

---

## 🧪 第三部分：测试（1 小时）

### 3.1 单元测试

```python
"""tests/test_agents/test_tools.py"""
import pytest
from src.research_agent.agents.tools import (
    search_web,
    summarize_text,
    save_research_report,
)


class TestSearchWeb:
    def test_search_basic(self):
        """测试基本搜索"""
        result = search_web.invoke({"query": "Python programming"})
        assert "搜索" in result or "result" in result.lower()

    def test_search_num_results(self):
        """测试结果数量限制"""
        result = search_web.invoke({
            "query": "test",
            "num_results": 3,
        })
        # 验证返回结果数量
        assert result is not None


class TestSummarizeText:
    def test_summarize_short(self):
        """测试短文本总结"""
        text = "这是一段测试文本。" * 10
        result = summarize_text.invoke({
            "text": text,
            "max_length": 100,
        })
        assert len(result) <= 100

    def test_summarize_empty(self):
        """测试空文本"""
        with pytest.raises(Exception):
            summarize_text.invoke({"text": ""})


class TestSaveReport:
    def test_save_markdown(self, tmp_path):
        """测试保存 MD 报告"""
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = save_research_report.invoke({
                "title": "Test Report",
                "content": "Test content",
                "format": "md",
            })
            assert "md" in result
        finally:
            os.chdir(original_dir)
```

### 3.2 集成测试

```python
"""tests/test_api/test_tasks.py"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.research_agent.main import app
from src.research_agent.models.user import User
from src.research_agent.models.task import Task, TaskStatus

client = TestClient(app)


@pytest.fixture
def test_user(db: Session):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User):
    """获取认证头"""
    from src.research_agent.security import create_access_token

    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


def test_create_task(auth_headers: dict):
    """测试创建任务"""
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "测试研究",
            "description": "这是一个测试",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "测试研究"
    assert data["status"] == "pending"


def test_list_tasks(auth_headers: dict):
    """测试列出任务"""
    response = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_task(auth_headers: dict, db: Session):
    """测试获取任务详情"""
    # 先创建任务
    task = Task(
        title="测试",
        description="测试描述",
        user_id=auth_headers["sub"],
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.get(
        f"/api/v1/tasks/{task.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["id"] == task.id
```

### 3.3 运行测试

```bash
# 运行所有测试
uv run pytest

# 带覆盖率
uv run pytest --cov=src/research_agent --cov-report=html

# 运行特定测试
uv run pytest tests/test_agents/ -v

# 运行集成测试
uv run pytest tests/test_api/ -v
```

---

## 🚀 第四部分：部署（1 小时）

### 4.1 Docker 配置

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 复制项目
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# 安装依赖
RUN uv sync --frozen

# 设置环境变量
ENV PYTHONPATH=/app/src

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "uvicorn", "src.research_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/research
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=research
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 4.2 部署脚本

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 开始部署..."

# 构建
docker-compose build

# 运行迁移
docker-compose run --rm api uv run alembic upgrade head

# 启动服务
docker-compose up -d

echo "✅ 部署完成！"
echo "访问：http://localhost:8000/docs"
```

### 4.3 生产环境配置

```bash
# .env.production
DEBUG=false
DATABASE_URL=postgresql://user:pass@prod-db:5432/research
SECRET_KEY=<生成强随机密钥>
OPENAI_API_KEY=<生产密钥>
```

---

## ✅ 第五部分：检查清单

### 功能检查

- [ ] 用户可以注册/登录
- [ ] 可以创建研究任务
- [ ] Agent 自动执行研究
- [ ] 实时查看进度
- [ ] 查看研究结果

### 代码质量

```bash
# 类型检查
uv run pyright .

# 代码格式化
uv run ruff format .

# Lint 检查
uv run ruff check .

# 测试
uv run pytest --cov=src
```

---

## 🎓 总结

恭喜你完成了一周的 Python 学习！

### 你学到了什么

| 天数 | 主题 | 核心技能 |
|------|------|---------|
| Day 1 | 环境 + 语法 | uv, Ruff, 推导式，解包 |
| Day 2 | OOP + 高级特性 | 装饰器，上下文管理器，类型注解 |
| Day 3 | FastAPI | RESTful API, Pydantic, SQLModel |
| Day 4 | LangChain | Prompt, Chain, RAG |
| Day 5 | Agent | Tools, ReAct, LangGraph |
| Day 6 | 前端 | HTMX, Streamlit |
| Day 7 | 综合项目 | 完整应用开发 |

### 下一步建议

1. **深入 LangChain**：学习 LangGraph 高级用法
2. **学习异步**：深入理解 asyncio
3. **前端进阶**：系统学习 React/Vue
4. ** DevOps**：学习 CI/CD、监控、日志

### 参考资源

- [Python 官方文档](https://docs.python.org/3/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [LangChain 文档](https://python.langchain.com/)
- [Real Python](https://realpython.com/)

---

**保持学习，持续进步！🎉**
