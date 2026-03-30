# Day 04 - LangChain Agent 开发基础

> 目标：掌握大模型应用开发框架，构建智能问答 Agent

---

## 📋 今日学习目标

- [ ] 理解 LangChain 核心架构
- [ ] 掌握 Prompt Template 设计
- [ ] 理解 LCEL（LangChain Expression Language）
- [ ] 实现 Chain 与 Memory 机制
- [ ] 集成向量数据库实现 RAG

---

## 📦 第一部分：LangChain 简介与环境搭建（30 分钟）

### 1.1 LangChain 核心概念

```
┌─────────────────────────────────────────────────────────┐
│                    LangChain 架构                       │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Models    │    │   Prompts   │    │   Memory    │ │
│  │  (LLM/Chat) │    │ (Templates) │    │ (History)   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│           │                │                │           │
│           └────────────────┼────────────────┘           │
│                            ▼                            │
│                   ┌─────────────┐                       │
│                   │   Chains    │                       │
│                   │  (Workflows)│                       │
│                   └─────────────┘                       │
│                            │                            │
│           ┌────────────────┼────────────────┐           │
│           ▼                ▼                ▼           │
│     ┌──────────┐    ┌──────────┐    ┌──────────┐       │
│     │  Agents  │    │  RAG     │    │  Tools   │       │
│     │ (决策)   │    │ (检索)   │    │ (工具)   │       │
│     └──────────┘    └──────────┘    └──────────┘       │
└─────────────────────────────────────────────────────────┘
```

### 1.2 环境搭建

```bash
# 安装核心依赖
uv add langchain langchain-core langchain-community

# 安装 LLM 提供商
uv add langchain-openai  # OpenAI
# 或
uv add langchain-anthropic  # Anthropic
# 或
uv add langchain-ollama  # 本地 Ollama

# 安装向量数据库
uv add chromadb  # 轻量级
# 或
uv add pinecone-client  # 云端

# 安装文本处理
uv add langchain-text-splitters

# 配置环境变量（.env 文件）
echo "OPENAI_API_KEY=sk-xxx" >> .env
echo "ANTHROPIC_API_KEY=sk-ant-xxx" >> .env
```

### 1.3 第一个 LLM 调用

```python
"""src/python_mastery/llm_basic.py"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件


def basic_chat():
    """基础对话"""
    # 初始化模型
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,  # 创造性：0=确定，1=随机
        max_tokens=None,
    )

    # 构建消息
    messages = [
        SystemMessage(content="你是一个有帮助的助手。"),
        HumanMessage(content="你好，请介绍一下自己。"),
    ]

    # 调用
    response = llm.invoke(messages)
    print(response.content)

    # 流式输出
    for chunk in llm.stream(messages):
        print(chunk.content, end="", flush=True)


# 异步调用
async def async_chat():
    response = await llm.ainvoke(messages)
    print(response.content)
```

---

## 📝 第二部分：Prompt Template（1 小时）

### 2.1 基础模板

```python
"""src/python_mastery/prompts.py"""
from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser


def basic_prompt_template():
    """基础模板示例"""
    # 方法 1：使用 f-string（简单场景）
    template = "你是一个{role}。请回答以下问题：{question}"

    # 方法 2：使用 ChatPromptTemplate（推荐）
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的{role}，擅长{expertise}。"),
        ("human", "问题：{question}"),
    ])

    # 格式化
    formatted = prompt.format(
        role="Python 开发者",
        expertise="Web 开发",
        question="FastAPI 和 Flask 有什么区别？"
    )
    print(formatted)


def translation_prompt():
    """翻译提示词"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的翻译，将{text}翻译成{target_language}。"),
        ("human", "{input_text}"),
    ])

    # 创建链
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o")
    chain = prompt | llm | StrOutputParser()

    # 执行
    result = chain.invoke({
        "target_language": "中文",
        "input_text": "Hello, how are you today?",
    })
    print(result)  # 你好，你今天怎么样？
```

### 2.2 Few-Shot Prompting

```python
from langchain_core.prompts import FewShotChatMessagePromptTemplate

def few_shot_prompt():
    """Few-shot 示例学习"""
    # 示例
    examples = [
        {
            "input": "hi!",
            "output": "¡Hola!",
        },
        {
            "input": "bye!",
            "output": "¡Adiós!",
        },
        {
            "input": "thanks",
            "output": "¡Gracias!",
        },
    ]

    # 示例模板
    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{input}"),
        ("ai", "{output}"),
    ])

    # Few-shot 提示
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    # 完整提示
    final_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个西班牙语翻译助手。"),
        few_shot_prompt,
        ("human", "{input}"),
    ])

    # 创建链
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o")
    chain = final_prompt | llm | StrOutputParser()

    result = chain.invoke({"input": "good morning"})
    print(result)  # ¡Buenos días!
```

### 2.3 Prompt 设计最佳实践

```python
"""Prompt 设计原则"""

PROMPT_BEST_PRACTICES = """
1. **明确角色**：清晰定义 AI 的角色和职责
   - ❌ "回答问题"
   - ✅ "你是一位资深 Python 开发者，负责代码审查和技术咨询"

2. **提供上下文**：给出足够的背景信息
   - ❌ "修复这个 bug"
   - ✅ "这是一个 FastAPI 应用，用户报告登录接口返回 500 错误"

3. **结构化输出**：明确期望的输出格式
   - ❌ "分析一下"
   - ✅ "请以 JSON 格式输出分析结果，包含：问题、原因、解决方案"

4. **分步骤**：复杂任务分解为多个步骤
   - ✅ "第一步：理解需求。第二步：设计架构。第三步：编写代码。"

5. **提供示例**：Few-shot 学习最有效
   - 给出 1-3 个输入输出示例

6. **设置约束**：明确边界条件
   - ✅ "只使用 Python 标准库"
   - ✅ "代码不超过 50 行"
"""
```

---

## 🔗 第三部分：LCEL 与 Chain（1 小时）

### 3.1 LCEL 基础

```python
"""src/python_mastery/chains.py"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field


# LCEL 核心：使用 | 操作符组合组件
# Prompt | LLM | OutputParser

llm = ChatOpenAI(model="gpt-4o")


def simple_chain():
    """简单链"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个翻译助手。"),
        ("human", "将以下{text}翻译成{language}：{input}"),
    ])

    chain = prompt | llm | StrOutputParser()

    result = chain.invoke({
        "language": "法语",
        "input": "Hello, world!",
    })
    print(result)  # Bonjour, le monde!


def parallel_chain():
    """并行链"""
    from langchain_core.runnables import RunnableParallel

    # 同时执行多个任务
    branch_a = ChatPromptTemplate.from_template("总结：{text}")
    branch_b = ChatPromptTemplate.from_template("翻译成中文：{text}")
    branch_c = ChatPromptTemplate.from_template("提取关键词：{text}")

    combined = RunnableParallel(
        summary=branch_a | llm | StrOutputParser(),
        translation=branch_b | llm | StrOutputParser(),
        keywords=branch_c | llm | StrOutputParser(),
    )

    result = combined.invoke({
        "text": "Python 是一门高级编程语言，由 Guido van Rossum 创建。"
    })
    print(result)
```

### 3.2 结构化输出

```python
from typing import List, Optional


class AnalysisResult(BaseModel):
    """定义输出结构"""
    summary: str = Field(description="内容摘要")
    sentiment: str = Field(description="情感倾向", enum=["positive", "negative", "neutral"])
    confidence: float = Field(description="置信度，0-1 之间")
    keywords: List[str] = Field(description="关键词列表")


def structured_output_chain():
    """结构化输出链"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个文本分析助手。请分析以下文本。"),
        ("human", "{text}"),
    ])

    # 使用 Pydantic 输出解析器
    parser = JsonOutputParser(pydantic_object=AnalysisResult)

    chain = prompt | llm | parser

    result = chain.invoke({
        "text": "这家餐厅的食物非常美味，服务也很周到，但价格有点贵。"
    })

    # result 是 AnalysisResult 对象
    print(f"摘要：{result['summary']}")
    print(f"情感：{result['sentiment']}")
    print(f"关键词：{result['keywords']}")
```

### 3.3 条件链

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


def conditional_chain():
    """条件链"""
    def route(input: dict) -> str:
        if "代码" in input["question"] or "bug" in input["question"]:
            return "code_expert"
        elif "翻译" in input["question"]:
            return "translator"
        else:
            return "general"

    # 定义不同领域的 prompt
    code_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是资深程序员，请解答代码问题。"),
        ("human", "{question}"),
    ])

    translate_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是专业翻译，请准确翻译。"),
        ("human", "{question}"),
    ])

    general_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是通用助手，请友好回答。"),
        ("human", "{question}"),
    ])

    # 路由
    router = RunnableLambda(route)

    # 条件分支
    def select_prompt(route_name: str):
        prompts = {
            "code_expert": code_prompt,
            "translator": translate_prompt,
            "general": general_prompt,
        }
        return prompts.get(route_name, general_prompt)

    chain = (
        RunnablePassthrough()
        | router
        | select_prompt
        | llm
        | StrOutputParser()
    )

    result = chain.invoke({"question": "这段 Python 代码为什么报错？"})
    print(result)
```

---

## 🧠 第四部分：Memory 机制（30 分钟）

### 1.1 对话记忆

```python
"""src/python_mastery/memory.py"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage

llm = ChatOpenAI(model="gpt-4o")


def basic_memory():
    """基础对话记忆"""
    # 手动维护消息历史
    messages = [
        ("system", "你是一个友好的对话助手。"),
    ]

    # 第一轮
    messages.append(("human", "我叫小明。"))
    response1 = llm.invoke(messages)
    messages.append(("ai", response1.content))

    # 第二轮（模型记得之前的对话）
    messages.append(("human", "我叫什么名字？"))
    response2 = llm.invoke(messages)
    print(response2.content)  # 你叫小明。


def conversation_chain():
    """带记忆的对话链"""
    from langchain.chains import ConversationChain

    # 使用 LangChain 内置的对话链
    memory = ConversationBufferMemory()

    chain = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True,  # 打印调试信息
    )

    # 对话
    print(chain.predict(input="我叫小红，今年 25 岁。"))
    print(chain.predict(input="你喜欢什么颜色？"))
    print(chain.predict(input="我叫什么名字？"))  # 模型会记得


def custom_memory_chain():
    """自定义带记忆的链"""
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain.memory import ChatMessageHistory

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个有帮助的助手。"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    chain = prompt | llm | StrOutputParser()

    # 记忆管理
    message_history = ChatMessageHistory()

    def get_session_history(session_id: str) -> ChatMessageHistory:
        return message_history

    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    # 对话
    config = {"configurable": {"session_id": "user_1"}}

    print(with_message_history.invoke(
        {"input": "我叫小明"},
        config=config,
    ))

    print(with_message_history.invoke(
        {"input": "我的爱好是编程"},
        config=config,
    ))

    print(with_message_history.invoke(
        {"input": "我的爱好是什么？"},
        config=config,  # 模型会记得
    ))
```

### 1.2 记忆类型

```python
from langchain.memory import (
    ConversationBufferMemory,      # 完整历史
    ConversationBufferWindowMemory, # 滑动窗口
    ConversationTokenBufferMemory,  # Token 限制
    ConversationSummaryMemory,      # 摘要记忆
)


# 1. 缓冲记忆（保留所有历史）
buffer_memory = ConversationBufferMemory(
    return_messages=True,  # 返回 Message 对象
)

# 2. 滑动窗口（只保留最近 N 轮）
window_memory = ConversationBufferWindowMemory(
    k=5,  # 最近 5 轮
    return_messages=True,
)

# 3. Token 限制（自动修剪）
token_memory = ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=2000,  # 最多 2000 tokens
    return_messages=True,
)

# 4. 摘要记忆（自动总结）
summary_memory = ConversationSummaryMemory(
    llm=llm,
    return_messages=True,
)
```

---

## 🗄️ 第五部分：RAG 与向量数据库（1.5 小时）

### 5.1 RAG 原理

```
┌─────────────────────────────────────────────────────────┐
│                    RAG 流程                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │  文档    │ -> │  切分    │    │  嵌入    │         │
│  │ (PDF/Txt)│    │ (Chunks) │    │ (Embed)  │         │
│  └──────────┘    └──────────┘    └──────────┘         │
│                                       │                 │
│                                       ▼                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │  回答    │ <- │  生成    │ <- │  检索    │         │
│  │ (Answer) │    │ (Generate)│   │ (Retrieve)│        │
│  └──────────┘    └──────────┘    └──────────┘         │
│                                       ▲                 │
│                                       │                 │
│                              ┌───────────────┐          │
│                              │  向量数据库   │          │
│                              │  (Chroma)     │          │
│                              └───────────────┘          │
└─────────────────────────────────────────────────────────┘
```

### 5.2 文档加载与切分

```python
"""src/python_mastery/rag.py"""
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    PythonCodeTextSplitter,
)
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    DirectoryLoader,
    WebBaseLoader,
)


def load_documents():
    """加载文档"""
    # 从文件加载
    loader = TextLoader("data/document.txt", encoding="utf-8")
    documents = loader.load()

    # 从 PDF 加载
    pdf_loader = PyPDFLoader("data/manual.pdf")
    pdf_docs = pdf_loader.load()

    # 从目录加载多个文件
    dir_loader = DirectoryLoader(
        "data/docs/",
        glob="**/*.txt",
        loader_cls=TextLoader,
    )
    all_docs = dir_loader.load()

    # 从网页加载
    web_loader = WebBaseLoader([
        "https://example.com/page1",
        "https://example.com/page2",
    ])
    web_docs = web_loader.load()

    return documents


def split_documents(documents):
    """切分文档"""
    # 递归字符切分（推荐）
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,           # 每块 500 字符
        chunk_overlap=50,         # 重叠 50 字符
        length_function=len,
        separators=["\n\n", "\n", "。", "!", "?", "，", " ", ""],
    )

    chunks = text_splitter.split_documents(documents)

    print(f"原始文档数：{len(documents)}")
    print(f"切分后块数：{len(chunks)}")
    print(f"第一块内容：{chunks[0].page_content[:100]}...")

    return chunks
```

### 5.3 向量存储

```python
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


def create_vector_store(chunks: list[Document]):
    """创建向量存储"""
    # 初始化嵌入模型
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # 创建向量存储（内存）
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db",  # 持久化路径
    )

    return vectorstore


def persist_and_load():
    """持久化与加载"""
    embeddings = OpenAIEmbeddings()

    # 创建并保存
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db",
    )

    # 后续加载已存在的向量库
    loaded_vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
    )

    return loaded_vectorstore
```

### 5.4 检索与问答链

```python
from langchain.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


def retrieval_qa_chain(vectorstore):
    """检索问答链"""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # 自定义 prompt
    template = """基于以下上下文信息回答问题。如果你不知道答案，就说你不知道，不要编造答案。

上下文信息：
{context}

问题：{question}

回答："""

    prompt = ChatPromptTemplate.from_template(template)

    # 创建检索器
    retriever = vectorstore.as_retriever(
        search_type="similarity",  # 相似性搜索
        search_kwargs={"k": 3},    # 返回 3 个最相关的块
    )

    # 创建链
    qa_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return qa_chain


def conversational_retrieval_chain(vectorstore):
    """带对话历史的检索问答链"""
    from langchain.chains import ConversationalRetrievalChain

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    retriever = vectorstore.as_retriever()

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,  # 返回来源
        verbose=True,
    )

    return chain


# 使用示例
def demo_rag():
    """RAG 演示"""
    # 1. 准备文档
    docs = load_documents()
    chunks = split_documents(docs)

    # 2. 创建向量存储
    vectorstore = create_vector_store(chunks)

    # 3. 创建问答链
    qa = retrieval_qa_chain(vectorstore)

    # 4. 问答
    question = "LangChain 的主要功能是什么？"
    answer = qa.invoke(question)
    print(f"Q: {question}")
    print(f"A: {answer}")

    # 带历史的对话
    chat_chain = conversational_retrieval_chain(vectorstore)
    chat_history = []

    # 第一轮
    result1 = chat_chain({"question": "什么是 RAG？", "chat_history": chat_history})
    print(result1["answer"])
    chat_history.append(("什么是 RAG？", result1["answer"]))

    # 第二轮（模型记得上下文）
    result2 = chat_chain({"question": "它有什么优势？", "chat_history": chat_history})
    print(result2["answer"])
```

### 5.5 高级检索技巧

```python
def advanced_retrieval():
    """高级检索"""
    vectorstore = Chroma(persist_directory="./chroma_db")

    # 1. 相似度搜索
    similar_docs = vectorstore.similarity_search(
        query="Python 异步编程",
        k=3,
    )

    # 2. 相似度 + 阈值
    relevant_docs = vectorstore.similarity_search_with_score(
        query="异步编程",
        k=5,
        score_threshold=0.5,  # 只返回相似度>0.5 的
    )

    # 3. 最大边际相关性（去重）
    mmr_retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, "fetch_k": 10},
    )

    # 4. 元数据过滤
    filtered_docs = vectorstore.similarity_search(
        query="FastAPI",
        k=3,
        filter={"source": "api_docs.pdf"},  # 只从特定来源检索
    )

    # 5. 多查询检索（生成多个相关问题）
    from langchain.retrievers.multi_query import MultiQueryRetriever

    multi_query_retriever = MultiQueryRetriever.from_llm(
        retriever=vectorstore.as_retriever(),
        llm=llm,
    )
```

---

## 💻 第六部分：实战练习（1 小时）

### 任务：文档问答 Agent

实现一个能回答关于 Python 文档问题的 Agent：

```python
"""
需求：
1. 加载 Python 官方文档（本地文件或网页）
2. 切分文档并创建向量索引
3. 实现问答接口
4. 支持多轮对话
5. 显示引用来源

扩展功能：
- 支持多个文档来源
- 实现文档增量更新
- 添加引用高亮
"""
```

### 参考实现

```python
"""src/python_mastery/doc_qa_agent.py"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import ConversationBufferMemory


class DocQAAgent:
    def __init__(self, documents=None):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.embeddings = OpenAIEmbeddings()
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
        )

        if documents:
            self.index_documents(documents)

    def index_documents(self, documents):
        """索引文档"""
        # 切分
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )
        chunks = splitter.split_documents(documents)

        # 创建向量存储
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory="./chroma_docs",
        )

    def ask(self, question: str) -> dict:
        """提问"""
        # 构建 prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个文档问答助手。基于以下上下文回答问题。
如果上下文中没有答案，请诚实说明。
每个回答请附上引用来源。

上下文：{context}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ])

        # 检索
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})

        # 创建链
        chain = (
            {"context": retriever, "question": RunnablePassthrough(), "chat_history": lambda _: self.memory.chat_history}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        # 获取回答
        answer = chain.invoke(question)

        # 更新记忆
        self.memory.save_context({"input": question}, {"output": answer})

        return {"question": question, "answer": answer}
```

---

## ✅ 第七部分：今日检查清单

### 知识检查

- [ ] 理解 LangChain 的核心组件
- [ ] 能设计有效的 Prompt Template
- [ ] 掌握 LCEL 的链式组合
- [ ] 理解 Memory 的工作原理
- [ ] 能实现完整的 RAG 流程
- [ ] 理解向量检索的不同策略

### 代码检查

```python
# 测试基本功能
uv run python -m src.python_mastery.llm_basic
uv run python -m src.python_mastery.prompts
uv run python -m src.python_mastery.chains
uv run python -m src.python_mastery.rag
```

---

## 🚀 明日预告

**Day 05 - Agent 进阶与工具调用**

- Function Calling / Tool Use
- ReAct Agent
- LangGraph 状态机
- 多步任务规划

---

## 📝 参考资源

- [LangChain 官方文档](https://python.langchain.com/)
- [LCEL 文档](https://python.langchain.com/docs/expression_language/)
- [LangChain 食谱](https://python.langchain.com/docs/cookbook/)
- [Chroma 文档](https://docs.trychroma.com/)
