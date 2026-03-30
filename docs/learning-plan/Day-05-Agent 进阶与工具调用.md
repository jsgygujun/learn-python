# Day 05 - Agent 进阶与工具调用

> 目标：构建能调用外部工具的智能 Agent，实现复杂任务规划

---

## 📋 今日学习目标

- [ ] 理解 Agent 的工作原理
- [ ] 掌握 Function Calling / Tool Use
- [ ] 实现 ReAct Agent
- [ ] 掌握 LangGraph 状态机
- [ ] 构建多步任务规划 Agent

---

## 🤖 第一部分：Agent 基础（1 小时）

### 1.1 Agent 是什么

```
┌─────────────────────────────────────────────────────────┐
│                    Agent 架构                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐      │
│   │  用户    │ --> │  Agent   │ --> │  工具    │      │
│   │  请求    │     │  (大脑)  │     │  (执行)  │      │
│   └──────────┘     └──────────┘     └──────────┘      │
│                        │                   │            │
│                        ▼                   │            │
│                 ┌──────────────┐          │            │
│                 │   思考过程   │          │            │
│                 │  (Reasoning) │          │            │
│                 └──────────────┘          │            │
│                        │                   │            │
│                        ▼                   ▼            │
│                 ┌──────────────────────────────┐       │
│                 │      观察结果 → 最终回答     │       │
│                 └──────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

**Agent vs Chain 的区别**：
- **Chain**：预定义流程，固定步骤
- **Agent**：动态决策，自主选择工具和步骤

### 1.2 定义工具（Tools）

```python
"""src/python_mastery/agent_tools.py"""
from langchain_core.tools import tool
from typing import Optional
import requests


@tool
def search_web(query: str, num_results: int = 5) -> str:
    """搜索互联网获取最新信息。

    Args:
        query: 搜索关键词
        num_results: 返回结果数量

    Returns:
        搜索结果摘要
    """
    # 使用 Tavily API（专为 Agent 设计的搜索引擎）
    from tavily import TavilyClient

    client = TavilyClient(api_key="your-api-key")
    response = client.search(query, max_results=num_results)

    results = []
    for result in response["results"]:
        results.append(f"标题：{result['title']}\n内容：{result['content']}\n来源：{result['url']}")

    return "\n\n".join(results)


@tool
def calculate(expression: str) -> str:
    """计算数学表达式。

    Args:
        expression: 数学表达式，如 "2 + 2 * 3"

    Returns:
        计算结果
    """
    try:
        # 安全计算（不使用 eval）
        import ast
        import operator

        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
        }

        tree = ast.parse(expression, mode='eval')
        result = _eval_expr(tree.body, ops)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{e}"


def _eval_expr(node, ops):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        left = _eval_expr(node.left, ops)
        right = _eval_expr(node.right, ops)
        return ops[type(node.op)](left, right)
    else:
        raise TypeError("不支持的表达式")


@tool
def get_weather(city: str) -> str:
    """获取城市天气。

    Args:
        city: 城市名称

    Returns:
        天气信息
    """
    # 模拟天气 API
    # 实际使用 OpenWeatherMap 等 API
    weather_data = {
        "北京": "晴，温度：25°C，湿度：40%",
        "上海": "多云，温度：28°C，湿度：60%",
        "深圳": "小雨，温度：30°C，湿度：80%",
    }
    return weather_data.get(city, f"未找到城市 {city} 的天气信息")


@tool
def read_file(file_path: str) -> str:
    """读取文件内容。

    Args:
        file_path: 文件路径

    Returns:
        文件内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"读取失败：{e}"


@tool
def write_file(file_path: str, content: str) -> str:
    """写入文件内容。

    Args:
        file_path: 文件路径
        content: 文件内容

    Returns:
        操作结果
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功写入文件：{file_path}"
    except Exception as e:
        return f"写入失败：{e}"


def get_all_tools():
    """获取所有工具"""
    return [search_web, calculate, get_weather, read_file, write_file]
```

### 1.3 创建 Agent

```python
"""src/python_mastery/agent_basic.py"""
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

from .agent_tools import get_all_tools


def create_simple_agent():
    """创建简单 Agent"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    tools = get_all_tools()

    # 定义 prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个智能助手，可以调用工具帮助用户完成任务。
你有以下工具可用：
- search_web: 搜索互联网
- calculate: 计算数学表达式
- get_weather: 查询天气
- read_file: 读取文件
- write_file: 写入文件

请用中文回答。"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 创建 Agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    # 创建执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # 打印思考过程
        handle_parsing_errors=True,  # 处理解析错误
        max_iterations=10,  # 最大迭代次数
    )

    return agent_executor


def create_agent_with_memory():
    """创建带记忆的 Agent"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    tools = get_all_tools()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有帮助的助手。"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    # 记忆
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
    )

    return agent_executor


# 使用示例
def demo_agent():
    """Agent 演示"""
    agent = create_simple_agent()

    # 单轮对话
    response = agent.invoke({"input": "北京今天天气怎么样？"})
    print(response["output"])

    # 多轮对话（带记忆）
    agent_mem = create_agent_with_memory()

    agent_mem.invoke({"input": "我叫小明"})
    agent_mem.invoke({"input": "我的名字是什么？"})  # 会记得
```

---

## 🧠 第二部分：ReAct Agent（1 小时）

### 2.1 ReAct 原理

```
ReAct = Reasoning + Acting

思考 - 行动 - 观察 循环：

Thought: 我需要先搜索一下 Python 的最新版本
Action: search_web
Action Input: "Python latest version 2024"
Observation: Python 3.12 is the latest stable release...
Thought: 现在我知道了最新版本，可以回答用户了
Final Answer: Python 最新版本是 3.12...
```

### 2.2 ReAct 实现

```python
"""src/python_mastery/react_agent.py"""
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain import hub

from .agent_tools import get_all_tools


def create_react_agent_from_hub():
    """使用 LangChain Hub 中的 ReAct prompt"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    tools = get_all_tools()

    # 从 Hub 获取预定义的 ReAct prompt
    prompt = hub.pull("hwchase17/react-chat")

    # 创建 Agent
    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=15,
    )

    return agent_executor


def create_custom_react_agent():
    """自定义 ReAct prompt"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    tools = get_all_tools()

    # 自定义 prompt
    REACT_PROMPT = """你是一个智能助手。请使用以下格式回答问题：

Question: 用户的问题
Thought: 你应该始终思考下一步该做什么
Action: 采取的行动，只能是以下之一：{tool_names}
Action Input: 行动的输入参数
Observation: 行动的结果
...（可以重复 Thought/Action/Action Input/Observation 多次）
Thought: 我现在知道最终答案了
Final Answer: 对用户的最终回答

可用工具：
{tools}

开始！

Question: {input}
Thought:{agent_scratchpad}"""

    prompt = PromptTemplate.from_template(REACT_PROMPT)

    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors="请重新尝试，确保使用正确的工具格式。",
    )

    return agent_executor


# 使用示例
def demo_react():
    """ReAct 演示"""
    agent = create_react_agent_from_hub()

    # 复杂问题，需要多步推理
    response = agent.invoke({
        "input": "帮我查一下北京的天气，然后计算如果温度超过 25 度，温度的两倍是多少？"
    })
    print(response["output"])

    # 需要搜索和计算
    response2 = agent.invoke({
        "input": "Python 3.12 是什么时候发布的？距今天多少天？"
    })
    print(response2["output"])
```

### 2.3 自定义工具

```python
"""更复杂的工具示例"""
from langchain_core.tools import BaseTool, Tool
from pydantic import BaseModel, Field
from typing import Type


# 方法 1：使用 @tool 装饰器（推荐）
@tool("database_query")
def query_database(sql: str) -> str:
    """执行 SQL 查询数据库。

    Args:
        sql: SQL 查询语句

    Returns:
        查询结果
    """
    # 实际应用中连接真实数据库
    return f"执行 SQL: {sql}"


# 方法 2：继承 BaseTool（更灵活）
class CustomSearchTool(BaseTool):
    """自定义搜索工具"""
    name: str = "custom_search"
    description: str = "使用自定义搜索引擎搜索信息"

    def _run(self, query: str) -> str:
        """同步执行"""
        # 实现搜索逻辑
        return f"搜索结果：{query}"

    async def _arun(self, query: str) -> str:
        """异步执行"""
        return await self._run(query)


# 方法 3：带参数验证的工具
class AdvancedSearchInput(BaseModel):
    """搜索输入参数"""
    query: str = Field(description="搜索关键词")
    num_results: int = Field(default=5, description="结果数量", ge=1, le=20)
    date_range: Optional[str] = Field(None, description="日期范围")


class AdvancedSearchTool(BaseTool):
    """高级搜索工具"""
    name: str = "advanced_search"
    description: str = "高级搜索引擎，支持过滤和分页"
    args_schema: Type[BaseModel] = AdvancedSearchInput

    def _run(
        self,
        query: str,
        num_results: int = 5,
        date_range: Optional[str] = None,
    ) -> str:
        """执行搜索"""
        # 实现带参数的搜索
        filters = f", 日期：{date_range}" if date_range else ""
        return f"搜索 '{query}'，返回 {num_results} 条结果{filters}"


# 使用自定义工具
def create_agent_with_custom_tools():
    llm = ChatOpenAI(model="gpt-4o")
    tools = [
        query_database,
        CustomSearchTool(),
        AdvancedSearchTool(),
    ]

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)
```

---

## 🕸️ 第三部分：LangGraph 状态机（1.5 小时）

### 3.1 为什么需要 LangGraph

**Agent 的局限性**：
- 标准 Agent 是线性的：思考→行动→观察→回答
- 复杂任务需要：条件分支、循环、并行执行

**LangGraph 的优势**：
- 基于图的状态机
- 支持循环、分支、并行
- 更好的状态管理
- 可视化执行流程

### 3.2 LangGraph 基础

```python
"""src/python_mastery/langgraph_basic.py"""
from typing import TypedDict, Annotated, List, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages


# 定义状态
class AgentState(TypedDict):
    """图的状态"""
    messages: Annotated[List[BaseMessage], add_messages]
    iteration_count: int


# 定义节点
class Agent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o")

    def think(self, state: AgentState) -> AgentState:
        """思考节点"""
        messages = state["messages"]
        response = self.llm.invoke(messages)
        return {
            "messages": [response],
            "iteration_count": state["iteration_count"] + 1,
        }

    def should_continue(self, state: AgentState) -> Literal["action", "end"]:
        """条件判断：是否继续"""
        if state["iteration_count"] >= 5:
            return "end"
        return "action"

    def action(self, state: AgentState) -> AgentState:
        """行动节点"""
        # 模拟行动
        action_message = AIMessage(content="执行了某个行动")
        return {
            "messages": [action_message],
            "iteration_count": state["iteration_count"],
        }


def create_simple_graph():
    """创建简单状态图"""
    agent = Agent()

    # 创建图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("think", agent.think)
    workflow.add_node("action", agent.action)

    # 设置入口
    workflow.set_entry_point("think")

    # 添加边
    workflow.add_conditional_edges(
        "think",
        agent.should_continue,
        {
            "action": "action",
            "end": END,
        }
    )

    # 循环
    workflow.add_edge("action", "think")

    # 编译
    app = workflow.compile()

    return app


# 使用示例
def demo_graph():
    """图演示"""
    app = create_simple_graph()

    # 运行
    initial_state = {
        "messages": [HumanMessage(content="你好")],
        "iteration_count": 0,
    }

    for event in app.stream(initial_state):
        print(event)
```

### 3.3 完整的 Agent 图

```python
"""src/python_mastery/langgraph_agent.py"""
from typing import TypedDict, Annotated, List, Sequence
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import json


class AgentState(TypedDict):
    """Agent 状态"""
    messages: Annotated[Sequence[BaseMessage], add_messages]


class ToolCallingAgent:
    """工具调用 Agent"""

    def __init__(self, tools: List[BaseTool]):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.llm_with_tools = self.llm.bind_tools(tools)
        self.tools = tools

    def should_continue(self, state: AgentState) -> Literal["tools", END]:
        """判断是否需要调用工具"""
        messages = state["messages"]
        last_message = messages[-1]

        # 如果有工具调用，继续
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    def call_model(self, state: AgentState) -> AgentState:
        """调用模型"""
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}


def create_tool_agent_graph(tools: List[BaseTool]):
    """创建工具 Agent 图"""
    agent = ToolCallingAgent(tools)

    # 创建图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("agent", agent.call_model)
    workflow.add_node("tools", ToolNode(tools))

    # 设置入口
    workflow.set_entry_point("agent")

    # 添加条件边
    workflow.add_conditional_edges(
        "agent",
        agent.should_continue,
    )

    # 工具执行后回到 agent
    workflow.add_edge("tools", "agent")

    # 编译
    app = workflow.compile()

    return app


# 使用示例
def demo_langgraph_agent():
    """LangGraph Agent 演示"""
    from .agent_tools import get_all_tools

    tools = get_all_tools()
    app = create_tool_agent_graph(tools)

    # 运行
    messages = [HumanMessage(content="帮我查一下北京天气，然后写到一个文件里")]

    config = {"recursion_limit": 10}

    for event in app.stream({"messages": messages}, config=config):
        for node_name, node_output in event.items():
            print(f"=== 节点：{node_name} ===")
            print(node_output)

    # 获取最终结果
    final_state = app.invoke({"messages": messages})
    print("\n=== 最终回答 ===")
    print(final_state["messages"][-1].content)
```

---

## 📋 第四部分：多步任务规划（1 小时）

### 4.1 Plan-and-Execute 模式

```python
"""src/python_mastery/planning_agent.py"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List


class Step(BaseModel):
    """计划步骤"""
    step_number: int = Field(description="步骤序号")
    action: str = Field(description="要执行的动作")
    expected_output: str = Field(description="期望输出")


class Plan(BaseModel):
    """完整计划"""
    goal: str = Field(description="任务目标")
    steps: List[Step] = Field(description="步骤列表")


def create_planner():
    """创建规划器"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # 规划 prompt
    planner_prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个任务规划专家。请将复杂任务分解为可执行的小步骤。

每个步骤应该：
1. 具体且可执行
2. 有明确的输出
3. 步骤之间有逻辑顺序"""),
        ("human", "任务：{task}"),
    ])

    parser = PydanticOutputParser(pydantic_object=Plan)

    chain = planner_prompt | llm | parser

    return chain


def create_executor(tools):
    """创建执行器"""
    from .langgraph_agent import create_tool_agent_graph

    app = create_tool_agent_graph(tools)
    return app


class PlanAndExecuteAgent:
    """计划 - 执行 Agent"""

    def __init__(self, tools):
        self.planner = create_planner()
        self.executor = create_executor(tools)
        self.tools = tools

    def run(self, task: str) -> str:
        """执行任务"""
        # 1. 制定计划
        print("=== 制定计划 ===")
        plan = self.planner.invoke({"task": task})
        print(f"目标：{plan.goal}")
        for step in plan.steps:
            print(f"步骤 {step.step_number}: {step.action}")

        # 2. 执行计划
        print("\n=== 执行计划 ===")
        messages = [HumanMessage(content=f"任务：{task}\n\n计划：{plan}")]

        for step in plan.steps:
            print(f"\n执行步骤 {step.step_number}: {step.action}")
            messages.append(HumanMessage(content=step.action))

            result = self.executor.invoke({"messages": messages})
            messages = result["messages"]

            print(f"步骤 {step.step_number} 完成")

        # 3. 汇总结果
        print("\n=== 汇总结果 ===")
        messages.append(HumanMessage(content="任务已完成，请总结结果。"))
        final_result = self.executor.invoke({"messages": messages})

        return final_result["messages"][-1].content


# 使用示例
def demo_planning_agent():
    """规划 Agent 演示"""
    from .agent_tools import get_all_tools

    tools = get_all_tools()
    agent = PlanAndExecuteAgent(tools)

    task = "帮我研究一下 2024 年 Python 的发展趋势，写一份总结报告保存到文件"

    result = agent.run(task)
    print(f"\n最终结果：{result}")
```

### 4.2 多 Agent 协作

```python
"""多 Agent 协作示例"""
from typing import Dict
from langchain_core.messages import HumanMessage


class MultiAgentSystem:
    """多 Agent 系统"""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o")
        self.agents = self._create_agents()

    def _create_agents(self) -> Dict:
        """创建不同角色的 Agent"""
        return {
            "researcher": self._create_researcher(),
            "writer": self._create_writer(),
            "reviewer": self._create_reviewer(),
        }

    def _create_researcher(self):
        """研究员 Agent"""
        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是研究员，负责收集和整理信息。"),
            ("human", "{input}"),
        ])
        return prompt | self.llm

    def _create_writer(self):
        """作家 Agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是作家，负责将研究结果整理成文章。"),
            ("human", "{input}"),
        ])
        return prompt | self.llm

    def _create_reviewer(self):
        """审核员 Agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是审核员，负责检查文章质量。"),
            ("human", "{input}"),
        ])
        return prompt | self.llm

    def run(self, task: str) -> str:
        """多 Agent 协作流程"""
        # 1. 研究
        research_result = self.agents["researcher"].invoke({
            "input": f"请研究：{task}"
        })

        # 2. 写作
        article = self.agents["writer"].invoke({
            "input": f"基于以下研究结果写文章：{research_result.content}"
        })

        # 3. 审核
        review = self.agents["reviewer"].invoke({
            "input": f"请审核以下文章：{article.content}"
        })

        return review.content
```

---

## 💻 第五部分：实战练习（1 小时）

### 任务：智能研究助手

实现一个能完成研究任务的 Agent：

```python
"""
需求：
1. 接收研究主题
2. 自动制定研究计划
3. 使用搜索工具收集信息
4. 整理并生成研究报告
5. 保存到本地文件

功能要求：
- 支持多轮对话细化需求
- 显示研究进度
- 输出结构化的报告
- 处理错误和重试
"""
```

### 项目结构

```
src/python_mastery/
├── agent_tools.py          # 工具定义
├── agent_basic.py          # 基础 Agent
├── react_agent.py          # ReAct Agent
├── langgraph_agent.py      # LangGraph Agent
├── planning_agent.py       # 规划 Agent
└── research_assistant.py   # 研究助手（实战）
```

---

## ✅ 第六部分：今日检查清单

### 知识检查

- [ ] 理解 Agent 的工作原理
- [ ] 能定义自定义工具
- [ ] 掌握 ReAct 模式
- [ ] 理解 LangGraph 状态机
- [ ] 能实现多步任务规划
- [ ] 了解多 Agent 协作

### 代码检查

```bash
# 测试 Agent 功能
uv run python -m src.python_mastery.agent_basic
uv run python -m src.python_mastery.react_agent
uv run python -m src.python_mastery.langgraph_agent
uv run python -m src.python_mastery.planning_agent
```

---

## 🚀 明日预告

**Day 06 - 前端基础与全栈开发**

- HTMX + FastAPI 快速构建前端
- Streamlit 数据应用
- React/Vue 基础

---

## 📝 参考资源

- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [LangChain Hub](https://smith.langchain.com/hub)
- [Tavily API](https://tavily.com/)
