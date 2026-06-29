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

# LangChain Core Concepts - LCEL and Runnable Chains
uv run core_concepts.py

# Working with LLMs in LangChain - Multi Providers Configuration
uv run working_with_llms.py

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

## Prompt Message and Message Types

### 1. Prompt Template 是什麼？

* Prompt 的**模板**，類似表單或餅乾模具（Cookie Cutter）。
* 先定義固定內容，再用**變數（Variables）**填入不同值。
* 例如：

```text
Tell me a {adjective} joke about {topic}.
```

填入：

* adjective = funny
* topic = cats

得到：

```text
Tell me a funny joke about cats.
```

---

### 2. 為什麼使用 Template？

* **可重複使用（Reusable）**：定義一次，重複使用。
* **封裝（Encapsulation）**：Prompt 結構集中管理。
* **容易維護（Maintainability）**：修改模板即可影響所有使用處。

---

### 3. Multi-Message Template

除了單一 Prompt，還可以建立多種 Message：

```text
System:
You are a {role}.
Always be {tone}.

Human:
{question}
```

例如：

* role = tutor
* tone = encouraging
* question = Explain recursion.

會產生：

* **System Message**：You are a helpful tutor. Always be encouraging.
* **Human Message**：Explain recursion.

好處是能同時設定 AI 的角色與使用者問題。

---

### 4. LangChain 的 Message Types

* **System Message**：設定 AI 的角色、行為（Persona）。
* **Human Message**：使用者輸入的問題或任務。
* **AI Message**：AI 回覆內容。
* **Tool Message**：工具/API/資料庫回傳的結果。

常見流程：

```text
┌────────┐   ┌────────┐   ┌──────┐   ┌────────┐   ┌──────┐   ┌────────┐   ┌──────┐
│ System │ → │ Human  │ → │  AI  │ → │ Human  │ → │  AI  │ → │  Tool  │ → │  AI  │
└────────┘   └────────┘   └──────┘   └────────┘   └──────┘   └────────┘   └──────┘
```

---

#### 5. Few-shot Prompting（少樣本提示）

透過**提供幾個範例**讓 AI 學習規律，而不是寫死規則。

例如：

```text
Happy → Sad
Tall → Short
Hot → Cold
```

之後輸入：

```text
Fast
```

AI 就能**推論**：

```text
Slow
```

通常提供 **2～5 個範例**就足夠。

---

#### 6. Prompt Composition（Prompt 組合）

將多個可重用的 Prompt 元件組合成完整 Prompt。

例如：

```text
System Prompt
You are a {role}.

User Prompt
{question}
```

組合後：

```text
You are a tutor.

Explain recursion.
```

---

### 核心觀念（一句話）

> **LangChain 利用 Prompt Template、Message、Few-shot Prompting 與 Prompt Composition，讓 Prompt 具備「可重用、模組化、易維護」的特性，更容易建立大型 AI 應用與 AI Agent。**

---

### Hands-on Exercises

```bash
source .venv/Scripts/activate

cd langchain-course/
pyenv global 3.12.10
pyenv local 3.12.10

# Prompt Templates and Messages - Deep Dive
uv run prompt_messages.py

```

## Why Output Parsers?

### ❌ The Problem *String*

> "The person is named Alex and they are 25 years old and work as a developer..."

---

### ✅ The Solution **→ Parser →** *Structured*

| Field  | Value         |
|--------|---------------|
| name:  | "Alex"        |
| age:   | 25            |
| job:   | "developer"   |

---

### Key Benefits

- **Parse JSON, lists, objects**
- **Handle errors gracefully**
- **Enable downstream processing**
- **Type-safe with Pydantic**

### LLM Parsers LangChain Output Parsers（2026 版）

> 📌 **官方定位（LangChain v1，2026）**
> 現今多數 LLM（OpenAI、Anthropic Claude、xAI Grok 等）已**原生支援結構化輸出**。能用模型原生能力時，官方建議優先用 **`model.with_structured_output()`**，而非手動接 output parser。
> `*OutputParser` 主要保留給：**不支援原生結構化輸出的模型**，或需要**額外處理 / 驗證**的場景。

#### 首選：with_structured_output()（含型別驗證）

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

structured_model = model.with_structured_output(Person)
result = structured_model.invoke("...")   # 回傳 Person 實例，age 已驗證為 int
```

- 自動選策略：原生支援的模型走 **ProviderStrategy**，其他走 **ToolStrategy（tool calling）**。
- 型別由 Pydantic 把關，但**型別安全 ≠ 語意正確**（填錯內容、型別卻對時不會報錯）。
- 在支援原生結構化輸出的模型上，with_structured_output() 比 PydanticOutputParser 可靠。

#### 仍適用 output parser 的場景

| 你要的輸出 | 用哪個 parser | 何時用 |
|---|---|---|
| 純字串 | `StrOutputParser` | LCEL chain 收尾取純文字，日常標配 |
| dict / JSON | `JsonOutputParser` | 模型不支援原生結構化輸出時最可靠的 JSON 方案 |
| 依自訂 schema 的結構化 dict | `StructuredOutputParser` | 輕量結構，**無型別驗證** |
| Pydantic 模型結構物件（**含型別驗證**） | `PydanticOutputParser` | 需驗證但模型不支援原生結構化輸出時的替代 |
| 逗號分隔清單 | `CommaSeparatedListOutputParser` | 解析 `a, b, c` → list |
| 日期 / 列舉 | `DatetimeOutputParser` / `EnumOutputParser` | 轉 datetime / 限定列舉值 |

- `StructuredOutputParser` **沒有型別驗證** — 它不保證 `age` 真的是整數。
- `PydanticOutputParser` 則用 Pydantic 模型，解析後得到一個**驗證過型別的物件**；`age` 若無法轉成整數會報錯（Pydantic 會先嘗試轉換，例如 `"25"` → `25`，無法轉換才報錯）。需要型別保證時用它。

### 速記

- **能用原生 → `with_structured_output(PydanticModel)`**（首選）。
- **模型不支援原生 / 要額外驗證 → 才用 parser**。
- `StrOutputParser` 例外：純取字串，在 `prompt | model | StrOutputParser()` 收尾仍最常用。
- 要不要型別驗證 → 要就 `PydanticOutputParser`，不要就 `StructuredOutputParser`。
```
