## LangChain 生态系统

### 核心包（Core Packages）

| 包名 | 功能描述 |
|------|----------|
| `langchain-core` | 核心抽象层与 LCEL（LangChain 表达式语言） |
| `langchain` | 智能体（Agents）、链（Chains）及高级 API |
| `langgraph` | 有状态智能体编排（Stateful Agent Orchestration） |
| `langsmith` | 追踪、评估与监控（Tracing, Evaluation, Monitoring） |
| `langserve` | 将链部署为 REST API |

### 集成包（Integration Packages）

| 包名 | 功能描述 |
|------|----------|
| `langchain-openai` | OpenAI 集成 |
| `langchain-anthropic` | Anthropic / Claude 集成 |
| `langchain-community` | 社区集成（多种第三方工具与服务） |

---

### 说明

- **核心包** 是 LangChain 框架的基础组件，提供链式调用、智能体构建、可观测性以及服务部署能力。
- **集成包** 用于对接各大主流大语言模型提供商及社区工具，方便开发者灵活切换和扩展不同的 AI 模型与服务。
- `langchain-core` 提供最底层的抽象定义，所有其他包均基于此构建。
- `langgraph` 专注于**有状态**的多智能体编排，支持复杂的工作流与循环逻辑。
- `langsmith` 提供全链路追踪与评估能力，是生产环境中监控 AI 系统的关键工具。

### When to Use What

| Component     | Use When...                                          |
|---------------|------------------------------------------------------|
| **LangChain** | Building chains, RAG, quick prototypes               |
| **LangGraph** | Stateful agents, loops, multi-agent, production      |
| **LangSmith** | Debugging, monitoring, evaluation                    |
| **LangServe** | Deploying as APIs                                    |


## Why Enterprise Bets on LangChain

| Feature              | Description                        |
|----------------------|------------------------------------|
| **Vendor-agnostic**  | Swap OpenAI ↔ Anthropic easily     |
| **LangSmith**        | Compliance and auditing            |
| **LangGraph**        | Durable, resumable workflows       |
| **Community**        | Active development, strong support |

> **Production-ready AI infrastructure**

## Environment Setup

| Component               | Details                              |
|-------------------------|--------------------------------------|
| **API Keys**            | OpenAI, Anthropic                    |
| **Python**              | UV (Modern Package Manager)          |
| **Verify Installation** | Run the verification python script   |
| **Code Editor**         | VS Code (your preference is okay…)   |

```bash
# Setup Development Environment
uv venv
source .venv/Scripts/activate
cd langchain-course/

pyenv global 3.12.10
pyenv local 3.12.10

uv pip install -r requirements.txt

# API Setup and Verification (OpenAI and Anthropic)
uv run main.py

# LangChain Core Concepts - LCEL and Runnable Chains
uv run core_concepts.py

# Working with LLMs in LangChain - Multi Providers Configuration
uv run working_with_llms.py

# Prompt Templates and Messages - Deep Dive
uv run prompt_templates.py

```

## LangCChain V.1 Architecture

```markdown
┌─────────────────────────────────────┐
│          Your Application           │
├─────────────────────────────────────┤
│     Chains & Agents  (langchain)    │
├─────────────────────────────────────┤
│  LCEL - LangChain Expression Lang.  │
├─────────────────────────────────────┤
│     Runnables  (langchain-core)     │
├─────────────────────────────────────┤
│  Model Integrations                 │
│  langchain-openai, langchain-       │
│  anthropic, etc.                    │
└─────────────────────────────────────┘
```
       
## 架构层级（从上到下）

### 🖥️ 你的应用（Your Application）
用户自行构建的业务逻辑层，调用下方所有组件来实现具体功能。

### 🔗 链与智能体（Chains & Agents）
**包：** `langchain`

将多个步骤串联成工作流（Chain），或赋予模型自主决策与工具调用能力（Agent）。

### ⚡ LCEL（LangChain 表达式语言）
**全称：** LangChain Expression Language
**包：** `langchain`

一种声明式的链式组合语法，使用管道符 `|` 将各组件串联，支持流式输出、批处理和异步执行。

### 🔧 可运行对象（Runnables）
**包：** `langchain-core`

LCEL 的核心抽象接口，所有组件（模型、提示词、解析器等）均实现 `**Runnable**` 协议，确保统一调用方式。

### 🤖 模型集成（Model Integrations）
**包：** `langchain-openai`、`langchain-anthropic` 等

最底层，负责对接各大 LLM 提供商的 API，屏蔽不同厂商的实现差异，对上层提供统一接口。

---

## Runnables —— 基础核心

> LangChain V.1 中的一切都是 "Runnable"（可运行对象）

| 组件 | 说明 |
|---|---|
| **Prompts（提示词）** | 是 Runnable |
| **Models（模型）** | 是 Runnable |
| **Output Parsers（输出解析器）** | 是 Runnable |
| **Chains（链）** | 是由多个 Runnable 组合而成的 Runnable |

---

**统一接口：** `invoke()`、`batch()`、`stream()`

## More Exercises: Runnables in Action

```bash
source .venv/Scripts/activate
cd langchain-course/

pyenv global 3.12.10
pyenv local 3.12.10
uv run core_concepts.py
```

## LCEL - The Pipe Operator

### Overview

**Chain components with the pipe operator `|`:**

```python
# Chain them with | (pipe operator)
chain = prompt | model | parser
```

> 💡 **The chain itself is also a Runnable!**

---

## Available Models (2026)

| Provider  | Model               | Best For              |
|-----------|---------------------|-----------------------|
| OpenAI    | `gpt-4o`            | Flagship, balanced    |
| OpenAI    | `gpt-4o-mini`       | Fast, cheap           |
| OpenAI    | `gpt-5.2`           | Latest, 400K context  |
| Anthropic | `claude-opus-4-5`   | Deep reasoning        |
| Anthropic | `claude-sonnet-4-5` | Balanced              |
| Anthropic | `claude-haiku-3-5`  | Fast, cheap           |
| Ollama    | `llama3.2, mistral` | Local, free           |

---

## Model Configuration

| Parameter | Description |
|---|---|
| `temperature` | 0 = deterministic / 1 = creative |
| `max_tokens` | Maximum output length (control response size) |
| `timeout` | Request timeout (prevent hanging) |
| `max_retries` | Retry on failure (handle transient errors) |

> 💡 Use `model_kwargs` for provider-specific parameters

---

## Streaming Responses

| Traditional (wait for full response) | Streaming (token-by-token) |
|---|---|
| ⏳ Waiting... (2-5 seconds) | `The \| quick \| brown \| fox \| ...` |
| → Full response appears at once | → Instant feedback, better UX |

## Benefits

| Immediate feedback | Better UX | Early termination |
|---|---|---|
| Users see response forming | Feels faster and more responsive | Stop if response goes wrong |

> 💡 Use `.stream()` method instead of `.invoke()`

---

## Cost Optimization

| | Strategy | Details |
|---|---|---|
| **1** | **Choose the Right Model** | gpt-4o-mini: $0.15/1M tokens<br>gpt-4o: $2.50/1M tokens<br>17x cost difference! |
| **2** | **Limit Output Tokens** | Set `max_tokens` to control response length and cost |
| **3** | **Use Caching** | Cache identical requests with `InMemoryCache` |

> 💰 **Pro Tip: Combine all three strategies**
>
> **Cheap model + limited tokens + caching = 50-100x cost reduction**
