# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run tests
uv run pytest

# Run single test file
uv run pytest tests/test_<name>.py -v

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
```

## Architecture

- **`src/python_mastery/`** - 核心源代码目录（Python 包）
- **`tests/`** - 测试代码目录
- **`docs/learning-plan/`** - 学习计划文档（Day-01 ~ Day-07）

项目采用标准的 Python 包结构，源代码位于 `src/` 下，测试位于 `tests/` 下。pytest 配置已设置 `pythonpath = ["src"]`，测试中直接使用 `from python_mastery.xxx import yyy` 导入。

## Tool Configuration

所有工具配置均在 `pyproject.toml` 中：

| 工具 | 用途 |
|------|------|
| **uv** | 包管理 + 虚拟环境 |
| **ruff** | Lint + Format（规则：E/F/I/N/W/UP/B） |
| **pyright** | 类型检查（strict 模式） |
| **pytest** | 测试框架（asyncio_mode = auto） |

Python 版本：3.12+
