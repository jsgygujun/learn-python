# Day 02 - 面向对象与高级特性

> 目标：掌握 Python 的 OOP 范式、装饰器、上下文管理器等高级特性

---

## 📋 今日学习目标

- [ ] 理解 Python 的类与对象模型
- [ ] 掌握装饰器的原理与应用
- [ ] 理解上下文管理器与 `with` 语句
- [ ] 掌握生成器与迭代器
- [ ] 熟练使用类型注解

---

## 🏗️ 第一部分：Python 的面向对象（1 小时）

### 1.1 类的定义与实例化

```python
# 基础类定义
class User:
    """用户类"""

    # 类变量（所有实例共享）
    species = "Homo sapiens"

    def __init__(self, name: str, age: int):
        """构造函数"""
        # 实例变量
        self.name = name  # public
        self._age = age   # protected（约定）
        self.__secret = "xxx"  # private（名称修饰）

    def greet(self) -> str:
        """实例方法"""
        return f"Hi, I'm {self.name}"

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """类方法（类似 Java 静态工厂方法）"""
        return cls(data["name"], data["age"])

    @staticmethod
    def is_adult(age: int) -> bool:
        """静态方法"""
        return age >= 18


# 使用
user = User("Alice", 25)
print(user.greet())  # Hi, I'm Alice

# 类方法
user2 = User.from_dict({"name": "Bob", "age": 30})

# 静态方法
print(User.is_adult(16))  # False
```

### 1.2 与 Java/Go 对比

| 概念 | Java | Go | Python |
|------|------|----|--------|
| **类定义** | `class User { }` | `type User struct { }` | `class User:` |
| **构造函数** | `public User() {}` | `NewUser()` | `__init__` |
| **self** | `this` | 无 | `self` |
| **访问控制** | `public/private` | 大小写 | `_ / __` |
| **类方法** | `static` | 无 | `@classmethod` |
| **继承** | `extends` | 无 | `class Child(Parent)` |

### 1.3 属性装饰器（@property）

```python
class Product:
    def __init__(self, price: float):
        self._price = price

    @property
    def price(self) -> float:
        """getter"""
        return self._price

    @price.setter
    def price(self, value: float):
        """setter"""
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = value

    @price.deleter
    def price(self):
        """deleter"""
        del self._price


# 使用
product = Product(100.0)
print(product.price)    # 100.0 - 像访问属性一样
product.price = 150.0   # 调用 setter
# product.price = -10   # 抛出 ValueError
```

### 1.4 魔术方法（Magic Methods）

```python
class Vector:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        """开发者字符串表示"""
        return f"Vector({self.x}, {self.y})"

    def __str__(self) -> str:
        """用户字符串表示"""
        return f"({self.x}, {self.y})"

    def __add__(self, other: "Vector") -> "Vector":
        """向量相加 v1 + v2"""
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other: object) -> bool:
        """相等比较 v1 == v2"""
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __len__(self) -> int:
        """len(v)"""
        return 2

    def __getitem__(self, index: int) -> int:
        """v[0], v[1]"""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Index out of range")

    def __iter__(self):
        """可迭代"""
        yield self.x
        yield self.y


# 使用
v1 = Vector(1, 2)
v2 = Vector(3, 4)

print(v1 + v2)      # (4, 6) - 调用 __add__
print(v1 == v2)     # False - 调用 __eq__
print(len(v1))      # 2 - 调用 __len__
print(v1[0])        # 1 - 调用 __getitem__
print(list(v1))     # [1, 2] - 调用 __iter__
```

### 1.5 继承与多重继承

```python
# 单继承
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        raise NotImplementedError


class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"


class Cat(Animal):
    def speak(self) -> str:
        return "Meow!"


# 多重继承（Mixin 模式）
class LoggerMixin:
    def log(self, message: str) -> None:
        print(f"[{self.__class__.__name__}] {message}")


class AuthenticatedUser(LoggerMixin, User):
    def __init__(self, name: str, age: int, token: str):
        super().__init__(name, age)
        self.token = token

    def authenticate(self) -> bool:
        self.log(f"Authenticating user {self.name}")
        return bool(self.token)


# 使用
dog = Dog("Buddy")
print(dog.speak())  # Woof!

auth_user = AuthenticatedUser("Alice", 25, "abc123")
auth_user.authenticate()  # [AuthenticatedUser] Authenticating...
```

### 1.6 数据类（@dataclass）

```python
from dataclasses import dataclass, field


@dataclass
class Point:
    """数据类 - 自动生成 __init__, __repr__, __eq__ 等"""
    x: int
    y: int
    z: int = 0  # 默认值


@dataclass
class Config:
    """使用 field() 自定义"""
    name: str
    values: list[str] = field(default_factory=list)
    _cache: dict = field(default_factory=dict, repr=False, init=False)


# 使用
p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1 == p2)  # True - 自动生成 __eq__
print(p1)        # Point(x=1, y=2, z=0) - 自动生成 __repr__

config = Config("app")
config.values.append("item")
```

---

## 🎨 第二部分：装饰器（Decorator）（1 小时）

### 2.1 装饰器原理

```python
# 装饰器本质是接受函数并返回函数的包装器

def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function call")
        result = func(*args, **kwargs)
        print("After function call")
        return result
    return wrapper


@my_decorator
def say_hello():
    print("Hello!")


# @my_decorator 等价于：
# say_hello = my_decorator(say_hello)

say_hello()
# Before function call
# Hello!
# After function call
```

### 2.2 实用的装饰器模式

#### 计时装饰器

```python
import functools
import time
from typing import Callable


def timing(func: Callable) -> Callable:
    """计算函数执行时间的装饰器"""
    @functools.wraps(func)  # 保留原函数的 __name__ 和文档
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} executed in {end - start:.4f}s")
        return result
    return wrapper


@timing
def slow_function():
    time.sleep(1)


slow_function()  # slow_function executed in 1.0012s
```

#### 重试装饰器

```python
def retry(max_attempts: int = 3, delay: float = 1.0):
    """失败重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


@retry(max_attempts=3, delay=0.5)
def unstable_api():
    import random
    if random.random() < 0.7:
        raise ConnectionError("Connection failed")
    return "Success!"
```

#### 缓存装饰器（Memoization）

```python
from functools import lru_cache


# 方法 1：使用内置 lru_cache
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# 方法 2：自定义缓存装饰器
def cache(func: Callable) -> Callable:
    """简单缓存装饰器"""
    _cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args not in _cache:
            _cache[args] = func(*args)
        return _cache[args]

    return wrapper


# 清除缓存
fibonacci.cache_clear()
```

#### 权限验证装饰器

```python
from functools import wraps


def require_auth(func: Callable) -> Callable:
    """需要认证的装饰器"""
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if not user.is_authenticated:
            raise PermissionError("Authentication required")
        return func(user, *args, **kwargs)
    return wrapper


def require_role(role: str):
    """需要特定角色的装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            if user.role != role:
                raise PermissionError(f"Requires {role} role")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator


# 使用
@require_auth
@require_role("admin")
def delete_user(user, user_id: int):
    pass
```

---

## 🔧 第三部分：上下文管理器（30 分钟）

### 3.1 with 语句原理

```python
# Java 的 try-with-resources
try (FileInputStream fis = new FileInputStream("file.txt")) {
    // 使用 fis
}

# Python 的 with 语句
with open("file.txt", "r") as f:
    content = f.read()
# 自动关闭文件，即使发生异常
```

### 3.2 实现上下文管理器

#### 方法 1：类实现

```python
from typing import Optional, TextIO


class ManagedFile:
    """文件上下文管理器"""

    def __init__(self, filename: str, mode: str = "r"):
        self.filename = filename
        self.mode = mode
        self.file: Optional[TextIO] = None

    def __enter__(self) -> TextIO:
        """进入时执行"""
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时执行"""
        if self.file:
            self.file.close()
        # 返回 True 会抑制异常，False 会让异常继续传播
        return False


# 使用
with ManagedFile("test.txt", "w") as f:
    f.write("Hello!")
```

#### 方法 2：contextlib 实现（推荐）

```python
from contextlib import contextmanager


@contextmanager
def managed_file(filename: str, mode: str = "r"):
    """使用生成器实现的上下文管理器"""
    f = open(filename, mode)
    try:
        yield f  # yield 之前的代码在 __enter__ 执行，之后在 __exit__ 执行
    finally:
        f.close()


# 使用
with managed_file("test.txt", "w") as f:
    f.write("Hello!")
```

### 3.3 实际应用场景

```python
from contextlib import contextmanager
import sqlite3


@contextmanager
def database_connection(db_path: str):
    """数据库连接上下文管理器"""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()  # 成功则提交
    except Exception:
        conn.rollback()  # 失败则回滚
        raise
    finally:
        conn.close()


# 使用
with database_connection("app.db") as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
```

---

## 🔄 第四部分：生成器与迭代器（30 分钟）

### 4.1 迭代器协议

```python
class CountDown:
    """自定义迭代器"""

    def __init__(self, start: int):
        self.start = start

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.start <= 0:
            raise StopIteration
        self.start -= 1
        return self.start


# 使用
for n in CountDown(5):
    print(n)  # 4, 3, 2, 1, 0
```

### 4.2 生成器函数

```python
def countdown(start: int):
    """生成器函数（更简洁）"""
    while start > 0:
        yield start
        start -= 1


# 使用
for n in countdown(5):
    print(n)  # 5, 4, 3, 2, 1


# 生成器表达式（类似推导式）
squares = (x * x for x in range(10))
print(sum(squares))  # 285
```

### 4.3 实际应用

```python
def read_lines(filename: str):
    """逐行读取大文件（惰性加载）"""
    with open(filename, "r") as f:
        for line in f:
            yield line.strip()


def fibonacci_generator():
    """无限生成器"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# 使用
import itertools

fib = fibonacci_generator()
first_10 = list(itertools.islice(fib, 10))
print(first_10)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

---

## 📝 第五部分：类型注解进阶（30 分钟）

### 5.1 基础类型

```python
from typing import (
    List, Dict, Tuple, Set, Optional, Union, Any,
    Callable, Iterable, Iterator, Generator,
    TypeVar, Generic
)

# 基础类型（Python 3.10+）
def process(
    name: str,
    age: int,
    scores: list[float],
    metadata: dict[str, any],
) -> dict[str, int]:
    return {"processed": 1}
```

### 5.2 高级类型

```python
from typing import TypeAlias, Literal

# 类型别名
UserId: TypeAlias = int | str
ScoreMap: TypeAlias = dict[str, list[float]]


# Literal 类型（限定值）
def set_status(status: Literal["active", "inactive", "pending"]) -> None:
    pass


# 联合类型
def parse(value: int | str | None) -> str:
    if value is None:
        return ""
    return str(value)


# 可空类型
def get_user(user_id: int) -> dict | None:
    """可能返回 None"""
    pass


# 函数类型
Callback = Callable[[str, int], bool]


def register_callback(callback: Callable[[str, int], bool]) -> None:
    pass
```

### 5.3 泛型

```python
from typing import TypeVar, Generic

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: list[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()


class Cache(Generic[K, V]):
    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value


# 使用
stack = Stack[int]()
stack.push(1)
stack.push(2)
print(stack.pop())  # 2

cache = Cache[str, int]()
cache.set("age", 25)
print(cache.get("age"))  # 25
```

### 5.4 Protocol（结构子类型）

```python
from typing import Protocol


class Drawable(Protocol):
    """定义协议（类似 Go 的 interface）"""
    def draw(self) -> str:
        ...


def render(shape: Drawable) -> str:
    return shape.draw()


class Circle:
    def draw(self) -> str:
        return "Drawing circle"


class Square:
    def draw(self) -> str:
        return "Drawing square"


# 无需显式继承 Protocol
render(Circle())  # Drawing circle
render(Square())  # Drawing square
```

---

## 💻 第六部分：实战练习（1 小时）

### 练习 1：实现一个完整的类

```python
"""src/python_mastery/bank_account.py"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Protocol


class TransactionListener(Protocol):
    def on_transaction(self, account: "BankAccount", amount: Decimal) -> None:
        ...


@dataclass
class Transaction:
    amount: Decimal
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""


class BankAccount:
    def __init__(
        self,
        account_number: str,
        owner: str,
        initial_balance: Decimal = Decimal("0"),
    ):
        self.account_number = account_number
        self.owner = owner
        self._balance = initial_balance
        self._transactions: list[Transaction] = []
        self._listeners: list[TransactionListener] = []

    @property
    def balance(self) -> Decimal:
        return self._balance

    def deposit(self, amount: Decimal, description: str = "") -> "BankAccount":
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self._balance += amount
        self._log_transaction(amount, description)
        self._notify_listeners()
        return self

    def withdraw(self, amount: Decimal, description: str = "") -> "BankAccount":
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        self._log_transaction(-amount, description)
        self._notify_listeners()
        return self

    def _log_transaction(self, amount: Decimal, description: str) -> None:
        transaction = Transaction(amount=amount, description=description)
        self._transactions.append(transaction)

    def add_listener(self, listener: TransactionListener) -> None:
        self._listeners.append(listener)

    def _notify_listeners(self) -> None:
        for listener in self._listeners:
            listener.on_transaction(self, self._balance)

    def get_statement(self) -> list[Transaction]:
        return self._transactions.copy()
```

### 练习 2：编写装饰器

```python
"""src/python_mastery/decorators.py"""
import functools
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)


def log_execution(func: Callable) -> Callable:
    """记录函数执行的装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Executing {func.__name__}")
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            raise
        finally:
            end = time.perf_counter()
            logger.info(f"{func.__name__} took {end - start:.4f}s")
    return wrapper


def rate_limit(calls: int, period: float):
    """限流装饰器"""
    from collections import deque

    def decorator(func: Callable) -> Callable:
        timestamps: deque = deque()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # 移除过期的时间戳
            while timestamps and timestamps[0] <= now - period:
                timestamps.popleft()

            if len(timestamps) >= calls:
                raise RuntimeError("Rate limit exceeded")

            timestamps.append(now)
            return func(*args, **kwargs)

        return wrapper
    return decorator
```

### 练习 3：编写测试

```python
"""tests/test_bank_account.py"""
import pytest
from decimal import Decimal
from python_mastery.bank_account import BankAccount, Transaction


class TestBankAccount:
    def test_initial_balance(self):
        account = BankAccount("123", "Alice")
        assert account.balance == Decimal("0")

    def test_deposit(self):
        account = BankAccount("123", "Alice")
        account.deposit(Decimal("100"))
        assert account.balance == Decimal("100")

    def test_withdraw(self):
        account = BankAccount("123", "Alice", Decimal("100"))
        account.withdraw(Decimal("50"))
        assert account.balance == Decimal("50")

    def test_insufficient_funds(self):
        account = BankAccount("123", "Alice", Decimal("50"))
        with pytest.raises(ValueError, match="Insufficient funds"):
            account.withdraw(Decimal("100"))

    def test_transaction_history(self):
        account = BankAccount("123", "Alice")
        account.deposit(Decimal("100"), "Initial deposit")
        account.withdraw(Decimal("50"), "Withdrawal")

        transactions = account.get_statement()
        assert len(transactions) == 2
        assert transactions[0].amount == Decimal("100")
        assert transactions[1].amount == Decimal("-50")
```

### 练习 4：运行验证

```bash
# 运行测试
uv run pytest tests/test_bank_account.py -v

# 类型检查
uv run pyright src/python_mastery/bank_account.py

# 格式化
uv run ruff format src/ tests/
```

---

## 📖 第七部分：晚间阅读（30 分钟）

### 阅读材料

1. **《Fluent Python》第 9-10 章**
   - 第 9 章：装饰器与闭包
   - 第 10 章：序列的迭代

2. **官方文档**
   - [Decorators](https://docs.python.org/3/glossary.html#term-decorator)
   - [Context Managers](https://docs.python.org/3/library/contextlib.html)
   - [Type Hints](https://docs.python.org/3/library/typing.html)

### 关键概念

- **装饰器链式调用**：多个装饰器的执行顺序
- **functools.wraps**：为什么需要它
- **生成器惰性求值**：处理大数据集的优势
- **Protocol 结构子类型**：与继承的区别

---

## ✅ 第八部分：今日检查清单

### 知识检查

- [ ] 理解 `@property` 的 getter/setter 用法
- [ ] 理解魔术方法的作用
- [ ] 能编写带参数的装饰器
- [ ] 理解 `with` 语句的工作原理
- [ ] 能区分类、迭代器、生成器
- [ ] 掌握类型注解的泛型用法

### 代码检查

```bash
# 测试通过
uv run pytest tests/ -v

# 类型检查无错误
uv run pyright .

# 无 lint 警告
uv run ruff check .
```

---

## 🚀 明日预告

**Day 03 - FastAPI 后端开发**

- FastAPI 基础架构
- Pydantic 数据验证
- 路由与依赖注入
- 异步编程 async/await
- RESTful API 设计

---

## 📝 参考资源

- [Real Python: Classes](https://realpython.com/python3-object-oriented-programming/)
- [Python Decorators](https://realpython.com/primer-on-python-decorators/)
- [Typing Module Docs](https://docs.python.org/3/library/typing.html)
- [Dataclasses](https://docs.python.org/3/library/dataclasses.html)
