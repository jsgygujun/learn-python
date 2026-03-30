# Learn Python

Python 7 天精通学习计划 - 从环境搭建到 FastAPI 全栈开发

## 项目简介

本项目是一个系统化的 Python 学习计划，专为有 Java/Go 背景的开发者设计。通过 7 天的学习，掌握 Python 核心语法、面向对象编程、FastAPI 框架和 Agent 开发。

## 技术栈

| 工具 | 用途 |
|------|------|
| **Python 3.12+** | 编程语言 |
| **uv** | 包管理 + 虚拟环境 |
| **FastAPI** | Web 框架 |
| **Pydantic** | 数据验证 |
| **Ruff** | 代码检查 + 格式化 |
| **Pyright** | 类型检查 |
| **pytest** | 测试框架 |

## 快速开始

### 安装依赖

```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步依赖
uv sync
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行单个测试文件
uv run pytest tests/test_data_tools.py -v

# 带覆盖率运行
uv run pytest --cov=src
```

### 代码质量检查

```bash
# Lint 检查
uv run ruff check .

# 格式化代码
uv run ruff format .

# 类型检查
uv run pyright .
```

### 运行主程序

```bash
uv run python main.py
```

## 项目结构

```
learn-python/
├── pyproject.toml          # 项目配置
├── uv.lock                 # 依赖锁定
├── .python-version         # Python 版本
├── src/
│   └── python_mastery/
│       ├── __init__.py     # 包标识
│       └── data_tools.py   # 数据处理工具
├── tests/
│   ├── __init__.py
│   └── test_data_tools.py  # 测试文件
└── docs/
    └── learning-plan/      # 学习计划文档
        ├── Day-01-Python 环境搭建与语法速成.md
        ├── Day-02-面向对象与高级特性.md
        ├── Day-03-FastAPI 后端开发.md
        ├── Day-04-LangChain Agent 开发基础.md
        ├── Day-05-Agent 进阶与工具调用.md
        ├── Day-06-前端基础与全栈开发.md
        └── Day-07-综合项目实战.md
```

## 学习计划

### Day 01 - Python 环境搭建与语法速成
- 安装 uv、pyenv 等工具链
- 理解 Python 与 Java/Go 的核心差异
- 掌握列表/字典推导式、切片、解包等惯用法

### Day 02 - 面向对象与高级特性
- 类与对象、魔术方法
- 装饰器原理与应用
- 上下文管理器与 `with` 语句
- 生成器与迭代器
- 类型注解进阶

### Day 03 - FastAPI 后端开发
- FastAPI 基础架构
- Pydantic 数据验证
- 路由与依赖注入
- 异步编程 async/await

### Day 04 - LangChain Agent 开发基础
- LangChain 核心概念
- Agent 基础架构
- 工具调用机制

### Day 05 - Agent 进阶与工具调用
- 复杂 Agent 流程
- 多工具协同
- 实际应用场景

### Day 06 - 前端基础与全栈开发
- 前端基础知识
- 前后端集成
- 全栈项目实践

### Day 07 - 综合项目实战
- 完整项目开发
- 最佳实践应用

## 开发指南

### 添加新依赖

```bash
# 运行时依赖
uv add package-name

# 开发依赖
uv add --dev package-name
```

### 创建新模块

在 `src/python_mastery/` 下创建新文件：

```python
"""模块描述"""
from typing import Any


def my_function(param: str) -> Any:
    """函数描述"""
    pass
```

### 编写测试

在 `tests/` 下创建对应的测试文件：

```python
"""测试描述"""
import pytest
from python_mastery.my_module import my_function


class TestMyFunction:
    def test_basic(self):
        assert my_function("input") == "expected"
```

## 参考资源

- [Python 官方文档](https://docs.python.org/3/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [uv 文档](https://docs.astral.sh/uv/)
- [Real Python](https://realpython.com/)
