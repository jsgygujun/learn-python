# Day 06 - 前端基础与全栈开发

> 目标：掌握 Python 全栈开发能力，构建完整的 Web 应用

---

## 📋 今日学习目标

- [ ] 理解现代前端开发方案选择
- [ ] 掌握 HTMX + FastAPI 快速开发
- [ ] 学会使用 Streamlit 构建数据应用
- [ ] 了解 React/Vue 基础概念
- [ ] 实现完整的全栈应用

---

## 🎯 第一部分：前端方案选择（30 分钟）

### 1.1 方案对比

| 方案 | 适用场景 | 学习曲线 | 开发速度 |
|------|---------|---------|---------|
| **HTMX** | 内部工具、Admin、简单交互 | ⭐ 低 | ⭐⭐⭐⭐⭐ |
| **Streamlit** | 数据应用、ML 演示、原型 | ⭐ 低 | ⭐⭐⭐⭐⭐ |
| **Gradio** | AI 模型演示、快速展示 | ⭐ 低 | ⭐⭐⭐⭐⭐ |
| **React** | 复杂 SPA、商业产品 | ⭐⭐⭐ 高 | ⭐⭐⭐ |
| **Vue** | 中小型应用、易上手 | ⭐⭐ 中 | ⭐⭐⭐⭐ |

### 1.2 推荐策略

```
对于 Python 后端开发者：

1. 快速原型/内部工具 → HTMX 或 Streamlit
2. 数据/AI 应用 → Streamlit 或 Gradio
3. 商业前端产品 → 学前端框架 (React/Vue)

本周学习重点：HTMX + Streamlit（最快产出）
```

---

## 🔨 第二部分：HTMX + FastAPI（2 小时）

### 2.1 HTMX 简介

**HTMX 理念**：在 HTML 中实现 AJAX、WebSocket、动画等，无需 JavaScript

```html
<!-- 传统方式需要 JavaScript -->
<button onclick="fetch('/api/data').then(r => r.text()).then(d => document.getElementById('result').innerHTML = d)">
    点击加载
</button>
<div id="result"></div>

<!-- HTMX 方式 -->
<button hx-get="/api/data" hx-target="#result">
    点击加载
</button>
<div id="result"></div>
```

### 2.2 环境搭建

```bash
# 安装依赖
uv add fastapi uvicorn jinja2 python-multipart
uv add itsdangerous  # CSRF 保护
uv add sqlalchemy sqlmodel  # 数据库

# 项目结构
mkdir -p src/python_mastery/fullstack/{templates,static}
```

### 2.3 第一个 HTMX 应用

```python
"""src/python_mastery/fullstack/main.py"""
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# 模板和静态文件
templates = Jinja2Templates(directory="src/python_mastery/fullstack/templates")
app.mount("/static", StaticFiles(directory="src/python_mastery/fullstack/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页"""
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "title": "HTMX 示例"},
    )


@app.get("/counter")
async def get_counter():
    """获取计数器（HTMX 片段）"""
    # 模拟计数器
    counter = 42
    return templates.TemplateResponse(
        "counter_partial.html",
        {"request": request, "counter": counter},
    )


@app.post("/increment")
async def increment_counter():
    """增加计数器"""
    # 模拟增加逻辑
    new_count = 43
    return templates.TemplateResponse(
        "counter_partial.html",
        {"request": request, "counter": new_count},
    )
```

### 2.4 模板文件

```html
<!-- src/python_mastery/fullstack/templates/home.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <!-- HTMX CDN -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <!-- Tailwind CSS（可选） -->
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen p-8">
    <div class="max-w-2xl mx-auto">
        <h1 class="text-3xl font-bold mb-6">HTMX 计数器示例</h1>

        <div class="bg-white rounded-lg shadow p-6">
            <div id="counter-container" hx-get="/counter" hx-trigger="load">
                <!-- 初始加载时从 /counter 获取内容 -->
                <div class="text-center">加载中...</div>
            </div>

            <button
                class="mt-4 bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
                hx-post="/increment"
                hx-target="#counter-container"
                hx-swap="innerHTML">
                点击 +1
            </button>
        </div>

        <!-- 其他 HTMX 示例 -->
        <div class="mt-8 bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-bold mb-4">表单示例</h2>

            <form
                hx-post="/search"
                hx-target="#search-results"
                hx-trigger="submit"
                class="space-y-4">

                <input
                    type="text"
                    name="query"
                    placeholder="搜索..."
                    class="w-full border rounded px-4 py-2"
                    required />

                <button
                    type="submit"
                    class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
                    搜索
                </button>
            </form>

            <div id="search-results" class="mt-4"></div>
        </div>
    </div>
</body>
</html>
```

```html
<!-- src/python_mastery/fullstack/templates/counter_partial.html -->
<!-- HTMX 片段：只返回需要更新的部分 -->
<div class="text-center">
    <p class="text-2xl font-bold">计数器：<span class="text-blue-500">{{ counter }}</span></p>
</div>
```

### 2.5 完整示例：用户管理

```python
"""src/python_mastery/fullstack/users.py"""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List, Optional

from ..api.deps import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/users", response_class=HTMLResponse)
async def list_users(request: Request, db: Session = Depends(get_db)):
    """用户列表页面"""
    users = db.exec(select(User)).all()
    return templates.TemplateResponse(
        "users/index.html",
        {"request": request, "users": users},
    )


@router.post("/users", response_class=HTMLResponse)
async def create_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    """创建用户（HTMX 表单提交）"""
    # 检查邮箱
    existing = db.exec(select(User).where(User.email == email)).first()
    if existing:
        return templates.TemplateResponse(
            "users/form_error.html",
            {"request": request, "error": "邮箱已注册"},
        )

    # 创建用户
    user = User(username=username, email=email)
    db.add(user)
    db.commit()

    # 返回更新后的列表
    users = db.exec(select(User)).all()
    return templates.TemplateResponse(
        "users/table.html",
        {"request": request, "users": users},
    )


@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(request: Request, user_id: int, db: Session = Depends(get_db)):
    """编辑用户表单（内联编辑）"""
    user = db.get(User, user_id)
    return templates.TemplateResponse(
        "users/edit_form.html",
        {"request": request, "user": user},
    )


@router.put("/users/{user_id}", response_class=HTMLResponse)
async def update_user(
    request: Request,
    user_id: int,
    username: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    """更新用户"""
    user = db.get(User, user_id)
    if not user:
        return HTMLResponse(status_code=404, content="用户不存在")

    user.username = username
    user.email = email
    db.add(user)
    db.commit()

    # 返回更新后的行
    return templates.TemplateResponse(
        "users/row.html",
        {"request": request, "user": user},
    )


@router.delete("/users/{user_id}", response_class=HTMLResponse)
async def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    user = db.get(User, user_id)
    if user:
        db.delete(user)
        db.commit()

    # 返回空内容（移除该行）
    return ""
```

### 2.6 HTMX 常用属性

```html
<!-- 核心属性 -->
hx-get="/api/data"          <!-- GET 请求 -->
hx-post="/api/create"       <!-- POST 请求 -->
hx-put="/api/update/1"      <!-- PUT 请求 -->
hx-delete="/api/delete/1"   <!-- DELETE 请求 -->

<!-- 目标元素 -->
hx-target="#result"         <!-- 替换指定元素 -->
hx-target="body"            <!-- 替换 body -->
hx-target="closest tr"      <!-- 最近的 tr 元素 -->

<!-- 交换方式 -->
hx-swap="innerHTML"         <!-- 替换内部 HTML（默认） -->
hx-swap="outerHTML"         <!-- 替换元素本身 -->
hx-swap="beforeend"         <!-- 追加到内部 -->
hx-swap="afterend"          <!-- 插入到后面 -->
hx-swap="delete"            <!-- 删除元素 -->
hx-swap="none"              <!-- 不替换（只执行脚本） -->

<!-- 触发条件 -->
hx-trigger="click"          <!-- 点击触发（默认） -->
hx-trigger="change"         <!-- 改变触发 -->
hx-trigger="keyup delay:500ms"  <!-- 键盘事件，延迟 500ms -->
hx-trigger="load"           <!-- 页面加载触发 -->
hx-trigger="every 2s"       <!-- 每 2 秒触发 -->

<!-- 其他 -->
hx-confirm="确定删除？"        <!-- 确认对话框 -->
hx-indicator=".spinner"     <!-- 加载指示器 -->
hx-disabled-elt="button"    <!-- 请求时禁用元素 -->
```

---

## 📊 第三部分：Streamlit 数据应用（2 小时）

### 3.1 Streamlit 简介

**特点**：
- 纯 Python 编写，无需 HTML/CSS/JS
- 适合数据应用、ML 演示
- 快速原型开发

### 3.2 环境搭建

```bash
uv add streamlit pandas plotly numpy
```

### 3.3 第一个 Streamlit 应用

```python
"""src/python_mastery/streamlit_app/app.py"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 页面配置
st.set_page_config(
    page_title="数据分析仪表板",
    page_icon="📊",
    layout="wide",
)

# 标题
st.title("📊 数据分析仪表板")

# 侧边栏
st.sidebar.header("设置")
chart_type = st.sidebar.selectbox(
    "图表类型",
    ["柱状图", "折线图", "散点图", "热力图"],
)

show_raw_data = st.sidebar.checkbox("显示原始数据", value=False)

# 生成示例数据
@st.cache_data  # 缓存数据生成
def generate_data(n_rows: int = 100) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=n_rows, freq="D")
    return pd.DataFrame({
        "日期": dates,
        "销售额": np.random.randint(1000, 10000, n_rows),
        "利润": np.random.randint(100, 2000, n_rows),
        "地区": np.random.choice(["华东", "华北", "华南", "华西"], n_rows),
    })

df = generate_data()

# 显示数据
col1, col2 = st.columns(2)

with col1:
    st.metric("总销售额", f"¥{df['销售额'].sum():,}")

with col2:
    st.metric("平均利润", f"¥{df['利润'].mean():.2f}")

# 图表
st.subheader("销售趋势")

if chart_type == "柱状图":
    fig = px.bar(df, x="日期", y="销售额", color="地区")
elif chart_type == "折线图":
    fig = px.line(df, x="日期", y="销售额", color="地区")
elif chart_type == "散点图":
    fig = px.scatter(df, x="销售额", y="利润", color="地区")
else:  # 热力图
    pivot = df.pivot_table(values="销售额", index="地区", columns=df["日期"].dt.day)
    fig = px.imshow(pivot, color_continuous_scale="RdYlGn")

st.plotly_chart(fig, use_container_width=True)

# 原始数据
if show_raw_data:
    st.subheader("原始数据")
    st.dataframe(df)

# 导出功能
csv = df.to_csv(index=False)
st.download_button(
    label="📥 下载 CSV",
    data=csv,
    file_name="sales_data.csv",
    mime="text/csv",
)
```

### 3.4 运行 Streamlit

```bash
# 运行应用
uv run streamlit run src/python_mastery/streamlit_app/app.py

# 自动在浏览器打开 http://localhost:8501
```

### 3.5 交互式应用

```python
"""src/python_mastery/streamlit_app/interactive.py"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("🤖 AI Agent 控制台")

# 会话状态（保持状态）
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_status" not in st.session_state:
    st.session_state.agent_status = "idle"

# 侧边栏 - 配置
with st.sidebar:
    st.header("Agent 配置")

    model = st.selectbox(
        "模型",
        ["gpt-4o", "gpt-3.5-turbo", "claude-3-sonnet"],
    )

    temperature = st.slider(
        "温度",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
    )

    st.divider()

    if st.button("清除对话", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# 主区域 - 对话
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 输入框
if prompt := st.chat_input("输入消息..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    # 模拟 AI 响应
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            # 这里调用真实的 Agent
            response = f"收到你的消息：{prompt}"
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# 任务管理
st.divider()
st.subheader("📋 任务管理")

col1, col2 = st.columns([3, 1])

with col1:
    new_task = st.text_input("添加任务")

with col2:
    if st.button("添加"):
        if new_task:
            if "tasks" not in st.session_state:
                st.session_state.tasks = []
            st.session_state.tasks.append({
                "task": new_task,
                "status": "pending",
                "created": datetime.now().isoformat(),
            })
            st.rerun()

# 显示任务列表
if "tasks" in st.session_state:
    for i, task in enumerate(st.session_state.tasks):
        col1, col2, col3 = st.columns([4, 1, 1])

        with col1:
            st.write(f"{task['task']}")

        with col2:
            status = task["status"]
            if status == "pending":
                if st.button("开始", key=f"start_{i}"):
                    st.session_state.tasks[i]["status"] = "running"
                    st.rerun()
            elif status == "running":
                st.write("⏳ 运行中")
            else:
                st.write("✅ 完成")

        with col3:
            if st.button("删除", key=f"del_{i}"):
                st.session_state.tasks.pop(i)
                st.rerun()
```

### 3.6 部署 Streamlit 应用

```bash
# 推送到 Streamlit Cloud
# 1. 将代码推送到 GitHub
# 2. 访问 https://streamlit.io/cloud
# 3. 连接 GitHub 仓库
# 4. 选择入口文件 app.py
# 5. 自动部署
```

---

## ⚛️ 第四部分：React/Vue 基础（1 小时）

### 4.1 何时需要前端框架

**使用 HTMX/Streamlit**：
- 内部工具/Admin
- 数据应用/原型
- 简单交互

**需要前端框架**：
- 复杂用户交互
- 离线/移动端
- 商业产品
- 复杂状态管理

### 4.2 React 快速上手

```jsx
// 使用 Create React App 或 Vite 创建项目
npm create vite@latest my-app -- --template react
cd my-app
npm install

// src/App.jsx - 简单示例
import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <h1>计数器：{count}</h1>
      <button onClick={() => setCount(count + 1)}>
        +1
      </button>
    </div>
  )
}

export default App
```

### 4.3 与 FastAPI 集成

```python
# FastAPI 服务 API
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/data")
async def get_data():
    return {"message": "Hello from FastAPI!"}
```

```jsx
// React 调用 API
import { useEffect, useState } from 'react'

function DataComponent() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('http://localhost:8000/api/data')
      .then(res => res.json())
      .then(setData)
  }, [])

  return <div>{data?.message}</div>
}
```

---

## 💻 第五部分：实战练习（1 小时）

### 任务：完整的全栈应用

选择一个实现：

**选项 A：HTMX + FastAPI**
```
任务管理系统
- 用户认证（登录/注册）
- CRUD 任务
- 拖拽排序（HTMX + SortableJS）
- 实时通知
```

**选项 B：Streamlit**
```
AI 助手仪表板
- 对话界面
- 任务历史
- 使用统计图表
- 配置管理
```

---

## ✅ 第六部分：今日检查清单

### 知识检查

- [ ] 理解不同前端方案的适用场景
- [ ] 掌握 HTMX 核心属性
- [ ] 能使用 Streamlit 构建数据应用
- [ ] 了解 React 基础概念
- [ ] 理解前后端分离架构

### 代码检查

```bash
# 测试 HTMX 应用
uv run uvicorn src.python_mastery.fullstack.main:app --reload

# 测试 Streamlit
uv run streamlit run src/python_mastery/streamlit_app/app.py
```

---

## 🚀 明日预告

**Day 07 - 综合项目实战**

- 完整项目架构设计
- 实现 AI Agent 应用
- 测试与部署

---

## 📝 参考资源

- [HTMX 官方文档](https://htmx.org/)
- [Streamlit 文档](https://docs.streamlit.io/)
- [FastAPI + HTMX 示例](https://fastapi.tiangolo.com/advanced/templates/)
- [React 官方教程](https://react.dev/learn)
