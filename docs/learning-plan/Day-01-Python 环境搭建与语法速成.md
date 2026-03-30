# Day 01 - Python 环境搭建与语法速成

> 目标：搭建现代化开发环境，掌握 Python 核心语法，能够编写 Pythonic 的代码
>
> 预计时间：4 小时（2h 环境 + 1.5h 语法 + 1h 实战）

---

## 📋 今日学习目标

- [ ] 安装并配置完整的 Python 开发工具链
- [ ] 理解 Python 与 Java/Go 的核心差异
- [ ] 掌握列表/字典推导式、切片、解包等惯用法
- [ ] 完成第一个 Python 项目并运行测试

---

## 🛠️ 第一部分：环境搭建（1 小时）

### 1.1 工具链概览

| 工具 | 用途 | Java/Go 对应物 |
|------|------|---------------|
| **pyenv** | Python 版本管理 | jenv / asdf |
| **uv** | 包管理 + 虚拟环境 | Maven + virtualenv |
| **Ruff** | Lint + Format | checkstyle + gofmt |
| **Pyright** | 类型检查 | tsc --noEmit |
| **pytest** | 测试框架 | JUnit / testing |

### 1.2 安装步骤

#### Step 1: 安装 pyenv（多版本管理）

```bash
# macOS
brew install pyenv pyenv-virtualenv

# Linux
curl https://pyenv.run | bash

# 添加到 ~/.zshrc
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
```

#### Step 2: 安装 uv（包管理器）

```bash
# 一行命令安装（推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证安装
uv --version
```

#### Step 3: 安装 Python 3.12

```bash
# 使用 pyenv 安装指定版本
pyenv install 3.12.0

# 设置为全局默认
pyenv global 3.12.0

# 验证
python --version  # Python 3.12.0
```

### 1.3 创建项目

```bash
# 创建新项目
mkdir -p python-mastery && cd python-mastery

# 用 uv 初始化项目
uv init

# 查看生成的文件
ls -la
# ├── pyproject.toml    # 项目配置（类似 pom.xml）
# ├── README.md
# ├── .python-version   # Python 版本锁定
# └── main.py
```

### 1.4 安装依赖（运行时 vs 开发）

<details>
<summary><strong>💡 注解：什么是运行时依赖和开发依赖？（点击展开）</strong></summary>

**运行时依赖**（Runtime Dependencies）：
- 你的程序**运行时必需**的库
- 生产环境部署时必须安装
- 例如：FastAPI（Web 框架）、Pydantic（数据验证）

**开发依赖**（Dev Dependencies）：
- **仅在开发/测试时**使用的工具
- 生产环境不需要安装
- 例如：pytest（测试）、ruff（代码检查）、black（格式化）

**为什么区分？**
```bash
# 生产环境只安装运行时依赖（减小镜像体积、加快部署）
uv sync --no-dev

# 开发环境安装全部依赖
uv sync  # 包含 dev-dependencies
```

**类比 Java/Go**：
| Python | Java | Go |
|--------|------|-----|
| `dependencies` | `<dependencies>` | `require` |
| `dev-dependencies` | `<scope>test</scope>` | `xxx_test.go` |

</details>

```bash
# 添加运行时依赖（程序运行必需）
uv add fastapi uvicorn pydantic

# 添加开发依赖（仅开发/测试时使用）
uv add --dev ruff pyright pytest pytest-asyncio pytest-cov

# 查看依赖树
uv pip tree

# 查看已安装的依赖
uv pip list
```

### 1.5 配置 pyproject.toml

<details>
<summary><strong>💡 注解：pyproject.toml 详解（点击展开）</strong></summary>

`pyproject.toml` 是 Python 项目的**标准配置文件**（类似 Java 的 `pom.xml` 或 Go 的 `go.mod`）。

**文件结构**：
- `[project]` - 项目元数据和运行时依赖
- `[tool.*]` - 各工具的配置文件
- `[build-system]` - 构建系统配置（uv 自动处理）

**版本锁定**：
- `uv.lock` - 锁定所有依赖的确切版本（类似 `package-lock.json`）
- 保证团队所有人和 CI/CD 使用完全相同的依赖版本

</details>

```toml
# ============================================
# 项目元数据配置
# ============================================
[project]
name = "python-mastery"           # 项目名称（Python 包名，用于 import）
version = "0.1.0"                 # 语义化版本号（major.minor.patch）
description = "Python 7 天精通计划"  # 项目描述
requires-python = ">=3.12"        # Python 版本要求（>=3.12 表示 3.12 及以上）

# 运行时依赖 - 生产环境必须安装的包
dependencies = [
    "fastapi>=0.109.0",           # Web 框架，>= 表示最小版本
    "uvicorn>=0.27.0",            # ASGI 服务器（运行 FastAPI）
    "pydantic>=2.5.0",            # 数据验证库
]

# ============================================
# uv 工具配置
# ============================================
[tool.uv]
# 开发依赖 - 仅在开发/测试时需要，生产环境不安装
dev-dependencies = [
    "ruff>=0.1.0",                # 代码检查 + 格式化（替代 flake8/black）
    "pyright>=1.1.0",             # 类型检查器（类似 TypeScript 的 tsc）
    "pytest>=7.4.0",              # 测试框架（类似 JUnit）
    "pytest-asyncio>=0.23.0",     # pytest 异步测试支持
    "pytest-cov>=4.1.0",          # 测试覆盖率插件
]

# ============================================
# Ruff 配置 - 代码风格检查
# ============================================
[tool.ruff]
line-length = 88                  # 每行最大字符数（PEP 8 推荐 79，Black 默认 88）
target-version = "py312"          # 目标 Python 版本，用于检查语法兼容性

[tool.ruff.lint]
select = [
    "E",   # pycodestyle 错误（如格式问题）
    "F",   # pyflakes 错误（如未使用的变量）
    "I",   # isort - 自动整理 import 顺序
    "N",   # pep8-naming - 命名规范检查
    "W",   # pycodestyle 警告
    "UP",  # pyupgrade - 自动升级旧语法到新语法
    "B",   # flake8-bugbear - 常见 bug 模式检测
]

# ============================================
# Pyright 配置 - 静态类型检查
# ============================================
[tool.pyright]
pythonVersion = "3.12"            # Python 版本
typeCheckingMode = "strict"       # 检查模式：off/basic/strict
include = ["src"]                 # 检查的目录
exclude = [
    "**/__pycache__",             # 排除 Python 缓存目录
    ".venv",                      # 排除虚拟环境
    "**/tests",                   # 排除测试文件（可选）
]

# ============================================
# pytest 配置 - 测试框架
# ============================================
[tool.pytest.ini_options]
asyncio_mode = "auto"             # 自动识别异步测试
testpaths = ["tests"]             # 测试文件所在目录
pythonpath = ["src"]              # 添加 src 到 Python 路径（关键！）
addopts = "-v --tb=short"         # 默认参数：-v 详细输出，--tb=short 简短错误追踪
```

**使用示例**：

```bash
uv run ruff check .              # 检查代码风格
uv run ruff format .             # 格式化代码
uv run pyright .                 # 类型检查
uv run pytest                    # 运行测试
uv run pytest --cov=src          # 带覆盖率
```

### 1.6 项目目录结构

<details>
<summary><strong>💡 注解：为什么需要 `__init__.py`？（点击展开）</strong></summary>

**`__init__.py` 的作用**：

1. **标识"这是一个 Python 包"**
   - 告诉 Python：`python_mastery` 是**包**（package），不是普通目录
   - 没有它，Python 无法 `import python_mastery.xxx`

2. **对比 Java/Go**：
   | 语言 | 包的标识方式 |
   |------|-------------|
   | **Python** | `__init__.py` 文件存在 |
   | **Java** | `package xxx;` 声明 + 目录结构 |
   | **Go** | `package xxx` 声明 + 目录结构 |

3. **`__init__.py` 的内容**：
   ```python
   # 方式 1：空文件（最常见，够用）
   # 什么都放，只是告诉 Python 这是包

   # 方式 2：暴露便利接口（进阶）
   from .data_tools import flatten, group_by

   __all__ = ["flatten", "group_by"]  # 定义公开 API
   __version__ = "0.1.0"
   ```

4. **命名空间包（了解即可）**：
   - Python 3.3+ 支持没有 `__init__.py` 的包（PEP 420）
   - 但**不推荐**：行为复杂，某些工具不兼容
   - **原则**：显式比隐式好（Python 之禅）

**快速创建**：
```bash
# 如果缺失，创建空文件
touch src/python_mastery/__init__.py

# 验证存在
ls src/python_mastery/__init__.py
```

</details>

<details>
<summary><strong>💡 注解：PyCharm 显示 'Unresolved reference' 如何解决？（点击展开）</strong></summary>

**问题**：PyCharm 显示 `Unresolved reference 'python_mastery'`

**原因**：PyCharm 默认不会读取 `pyproject.toml` 中的 `pythonpath` 配置，所以不知道 `src` 是源代码目录。

**解决方法**（推荐）：

1. **在 PyCharm 中右键点击 `src` 目录**
2. **选择 `Mark Directory as` → `Sources Root`**
3. `src` 图标会变成蓝色 📁

```
Before: 📁 src (灰色/黑色) - PyCharm 不识别
After:  📁 src (蓝色) ✅ - PyCharm 知道这是源代码目录
```

**效果**：
- ✅ 不再有红色波浪线
- ✅ `Cmd+B` 可以跳转到定义
- ✅ 自动补全正常工作

**备选方法**（如果上面不生效）：

1. **PyCharm** → **Settings** (macOS: **Preferences**)
2. **Languages & Frameworks** → **Python** → **Python Interpreter**
3. 添加 `src` 到 **Source Folders**

</details>

```
python-mastery/
├── pyproject.toml          # 项目配置
├── uv.lock                 # 依赖锁定（类似 package-lock.json）
├── .python-version         # Python 版本
├── .venv/                  # 虚拟环境（自动创建）
├── src/
│   └── python_mastery/
│       ├── __init__.py     # ⚠️ 必须有！标识这是 Python 包
│       └── main.py
├── tests/
│   ├── __init__.py         # 测试包（可选，但推荐）
│   └── test_main.py
└── README.md
```

**关键文件说明**：

| 文件 | 必须？ | 作用 |
|------|-------|------|
| `src/python_mastery/__init__.py` | ✅ 必须 | 标识 `python_mastery` 是包 |
| `tests/__init__.py` | ⚠️ 推荐 | 标识 `tests` 是包（某些工具需要） |
| `src/python_mastery/main.py` | - | 你的代码 |
| `tests/test_main.py` | - | 你的测试 |

---

<details>
<summary><strong>💡 进阶：一个项目可以有多个入口（应用）吗？（点击展开）</strong></summary>

**可以！** 一个 Python 仓库可以定义多个入口点（多个应用/程序）。

### 方式 1：使用 `project.scripts`（推荐）

```toml
# pyproject.toml
[project.scripts]
# 格式：命令名 = "模块路径：函数名"
api-server = "python_mastery.server:main"
worker = "python_mastery.worker:main"
cli-tool = "python_mastery.cli:main"
```

**安装后使用**：
```bash
uv sync                    # 安装
api-server                 # 启动 API 服务器
worker                     # 启动 Worker
cli-tool --help            # 使用 CLI 工具
```

### 方式 2：使用 `__main__.py`（子命令模式）

```bash
python -m python_mastery           # 主入口
python -m python_mastery.cli       # CLI 入口
python -m python_mastery.admin     # 管理入口
```

### 方式 3：独立脚本目录

```bash
python scripts/run_server.py
python scripts/migrate.py
```

### 对比 Java/Go

| 语言 | 多入口实现 |
|------|-----------|
| **Python** | `project.scripts` 或 `__main__.py` |
| **Java** | 多个 `public static void main()` 类 |
| **Go** | 多个 `cmd/*/main.go` 目录 |

</details>

---

## 📚 第二部分：Python vs Java/Go 核心差异（30 分钟）

### 2.1 语法对比表

| 特性 | Java | Go | Python |
|------|------|----|--------|
| **代码块** | `{ }` | `{ }` | 缩进 |
| **语句结束** | `;` | 无/自动 | 无/换行 |
| **变量声明** | `int x = 1` | `x := 1` | `x = 1` |
| **类型位置** | 类型在前 | 类型在后 | 可选注解 |
| **空值** | `null` | `nil` | `None` |
| **布尔值** | `true/false` | `true/false` | `True/False` |
| **逻辑运算** | `&& \|\| !` | `&& \|\| !` | `and or not` |
| **相等比较** | `==` | `==` | `==` (值) / `is` (身份) |
| **数组/列表** | `List<T>` | `[]T` | `list` |
| **Map** | `Map<K,V>` | `map[K]V` | `dict` |
| **Set** | `Set<T>` | 无内置 | `set` |

### 2.2 关键差异详解

#### 差异 1：动态类型 vs 静态类型

```python
# Python - 动态类型（运行时检查）
x = 1          # x 是 int
x = "hello"    # x 现在是 str，合法！

# Java - 静态类型（编译时检查）
int x = 1;
x = "hello";   // 编译错误！

# Python - 类型注解（可选，推荐）
x: int = 1
x: str = "hello"  # 类型检查器会警告
```

#### 差异 2：`==` vs `is`

```python
# == 比较值（类似 Java .equals()）
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)  # True - 值相同

# is 比较身份/引用（类似 Java ==）
print(a is b)  # False - 不同对象
```

#### 差异 3：None vs null

```python
# Python 的 None 是单例对象
def get_user():
    return None

# 正确写法
if user is None:  # 用 is，不用 ==
    pass
```

#### 差异 4：Truthy/Falsy 值

```python
# 以下值为 False
False, None, 0, 0.0, "", [], {}, set()

# Java 需要显式检查
if (str != null && !str.isEmpty()) { ... }

# Python 可以简写
if str:  # 非空即 True
    pass
```

---

## 🎯 第三部分：Python 惯用法（1.5 小时）

### 3.1 列表推导式（List Comprehension）⭐

```python
# Java 命令式
List<Integer> squares = new ArrayList<>();
for (int i = 1; i <= 10; i++) {
    squares.add(i * i);
}

# Python 命令式
squares = []
for i in range(1, 11):
    squares.append(i * i)

# Python 推导式（推荐）⭐
squares = [i * i for i in range(1, 11)]

# 带条件过滤
even_squares = [i * i for i in range(1, 11) if i % 2 == 0]

# 实际案例：提取用户 ID
users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
user_ids = [user["id"] for user in users]  # [1, 2]
```

### 3.2 字典推导式（Dict Comprehension）

```python
# 创建映射
squares = {x: x*x for x in range(5)}  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 反转字典
original = {"a": 1, "b": 2}
reversed_dict = {v: k for k, v in original.items()}  # {1: 'a', 2: 'b'}

# 过滤字典
data = {"name": "Alice", "age": 25, "secret": "xxx"}
public_data = {k: v for k, v in data.items() if k != "secret"}
```

### 3.3 切片（Slicing）

```python
nums = [0, 1, 2, 3, 4, 5]

# 基本切片
nums[0:3]    # [0, 1, 2] - 左闭右开
nums[:3]     # [0, 1, 2] - 从头开始
nums[3:]     # [3, 4, 5] - 到结尾
nums[:]      # 完整拷贝

# 负索引
nums[-1]     # 5 - 最后一个
nums[-3:]    # [3, 4, 5] - 最后三个
nums[:-1]    # [0, 1, 2, 3, 4] - 除了最后一个

# 步长
nums[::2]    # [0, 2, 4] - 每隔一个
nums[1::2]   # [1, 3, 5] - 奇数位置
nums[::-1]   # [5, 4, 3, 2, 1, 0] - 反转列表
```

### 3.4 解包（Unpacking）

```python
# 基本解包
x, y = 1, 2

# 交换变量（无需临时变量）
x, y = y, x

# 列表解包
first, *middle, last = [1, 2, 3, 4, 5]
# first=1, middle=[2,3,4], last=5

# 函数参数解包
def greet(name, age):
    print(f"{name} is {age}")

data = {"name": "Bob", "age": 30}
greet(**data)  # 字典解包为关键字参数

args = ["Bob", 30]
greet(*args)   # 列表解包为位置参数
```

### 3.5 字符串格式化（f-string）

```python
name = "Alice"
age = 25
pi = 3.14159

# f-string（Python 3.6+，推荐）
print(f"Hello, {name}!")
print(f"Next year: {age + 1}")
print(f"Pi: {pi:.2f}")  # 3.14

# 调试模式（Python 3.8+）
print(f"{name=}, {age=}")  # name='Alice', age=25
```

### 3.6 常用内置函数

```python
# enumerate - 遍历带索引
for i, item in enumerate(["a", "b", "c"]):
    print(f"{i}: {item}")

# zip - 并行遍历
names = ["Alice", "Bob"]
ages = [25, 30]
for name, age in zip(names, ages):
    print(f"{name} is {age}")

# any/all - 存在/全部
any(x > 0 for x in [-1, 0, 1])  # True
all(x > 0 for x in [1, 2, 3])   # True
```

---

## 💻 第四部分：实战练习（1 小时）

### 练习 1：数据处理工具

创建 `src/python_mastery/data_tools.py`：

```python
"""数据处理工具函数"""
from typing import Any


def flatten(nested: list[list[Any]]) -> list[Any]:
    """扁平化嵌套列表"""
    return [item for sublist in nested for item in sublist]


def group_by(items: list[dict], key: str) -> dict[Any, list[dict]]:
    """按指定键分组"""
    result: dict[Any, list[dict]] = {}
    for item in items:
        k = item[key]
        if k not in result:
            result[k] = []
        result[k].append(item)
    return result


def safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """安全获取嵌套字典的值"""
    for k in keys:
        if isinstance(data, dict):
            data = data.get(k, default)
        else:
            return default
    return data


if __name__ == "__main__":
    # 自测
    print(flatten([[1, 2], [3, 4], [5]]))
    print(group_by([{"name": "A", "dept": "Eng"}, {"name": "B", "dept": "Eng"}], "dept"))
```

### 练习 2：编写测试

创建 `tests/test_data_tools.py`：

```python
"""测试 data_tools 模块"""
import pytest
from python_mastery.data_tools import flatten, group_by, safe_get


class TestFlatten:
    def test_simple(self):
        assert flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]

    def test_empty(self):
        assert flatten([]) == []
        assert flatten([[]]) == []


class TestGroupBy:
    def test_basic(self):
        items = [{"name": "a", "type": "x"}, {"name": "b", "type": "y"}]
        result = group_by(items, "type")
        assert len(result["x"]) == 1
        assert len(result["y"]) == 1


class TestSafeGet:
    def test_nested(self):
        data = {"a": {"b": {"c": 1}}}
        assert safe_get(data, "a", "b", "c") == 1

    def test_missing(self):
        data = {"a": 1}
        assert safe_get(data, "b", default="N/A") == "N/A"
```

### 练习 3：运行测试和检查

<details>
<summary><strong>💡 注解：常见错误解决（点击展开）</strong></summary>

**错误：`ModuleNotFoundError: No module named 'python_mastery'`**

**原因**：Python 找不到 `python_mastery` 包，因为源文件在 `src/` 目录下。

**解决方法**：
```bash
# ✅ 方法 1：使用 pytest（推荐 - 会自动识别配置）
uv run pytest tests/test_data_tools.py -v

# ✅ 方法 2：设置 PYTHONPATH
PYTHONPATH=src uv run python tests/test_data_tools.py

# ✅ 方法 3：在 pyproject.toml 中配置
# [tool.pytest.ini_options]
# pythonpath = ["src"]
```

**检查项目结构**：
```bash
# 确认 __init__.py 存在
touch src/python_mastery/__init__.py
```

</details>

```bash
# 运行测试（推荐方式）
uv run pytest tests/test_data_tools.py -v

# 运行所有测试
uv run pytest

# 查看覆盖率
uv run pytest --cov=src/python_mastery

# 格式化代码
uv run ruff format src/ tests/

# Lint 检查
uv run ruff check src/ tests/

# 类型检查
uv run pyright src/
```

---

## ✅ 今日检查清单

### 环境检查

```bash
# 1. Python 版本正确
python --version  # Python 3.12.x

# 2. uv 可用
uv --version

# 3. 依赖已安装
uv pip list | grep -E "fastapi|ruff|pyright|pytest"
```

### 代码检查

```bash
# 所有测试通过
uv run pytest

# 无 lint 错误
uv run ruff check .

# 类型检查通过
uv run pyright .
```

### 知识检查

- [ ] 理解列表推导式语法
- [ ] 理解 `==` 和 `is` 的区别
- [ ] 理解 `None` 的正确比较方式
- [ ] 能用切片操作列表
- [ ] 能用解包简化代码
- [ ] 能用 f-string 格式化

---

## 🚀 明日预告

**Day 02 - 面向对象与高级特性**

- 类与对象：`__init__`, 继承，魔术方法
- 装饰器：理解并创建 decorator
- 上下文管理器：`with` 语句原理
- 生成器与迭代器
- 类型注解进阶

---

## 📝 参考资源

- [Python 官方文档](https://docs.python.org/3/)
- [Real Python](https://realpython.com/)
- [uv 文档](https://docs.astral.sh/uv/)
- [Ruff 规则列表](https://docs.astral.sh/ruff/rules/)
