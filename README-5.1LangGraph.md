# LangGraph

## LangGraph Solution

```mermaid
flowchart TD

    START((START))
    END((END))

    START --> A["Node A"]
    A --> B["Node B"]
    B --> C["Node C"]
    C --> END

    B -->|"Condition"| D["Node D"]
    D -->|"Retry / Loop"| B

    %% Shared State
    STATE[("Persistent State")]

    STATE -.-> A
    STATE -.-> B
    STATE -.-> C
    STATE -.-> D

    style STATE fill:#EDE7F6,stroke:#7E57C2,stroke-width:2px
    style START fill:#4CAF50,color:#fff
    style END fill:#F44336,color:#fff
    style A fill:#5B9BD5,color:#fff
    style B fill:#70AD47,color:#fff
    style C fill:#C58A5A,color:#fff
    style D fill:#7E57C2,color:#fff

```

## LangGraph Core capabilities

| Feature                   | What it means                                                                         | Example                                                                                                                      |
| ------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| ✅ **Cycles and Loops**    | A workflow can revisit previous nodes until a condition is satisfied.                 | An agent keeps searching and refining an answer until it finds enough evidence.                                              |
| ✅ **Persistent State**    | Shared state (memory) is maintained across all nodes throughout execution.            | User profile, chat history, retrieved documents, and intermediate results are available to every node.                       |
| ✅ **Conditional Routing** | The next node is selected dynamically based on the current state or LLM output.       | If confidence > 90%, return the answer; otherwise, perform another search or ask the user for clarification.                 |
| ✅ **Crash Recovery**      | Execution can resume from the last saved checkpoint after an interruption or failure. | If the server crashes during a 20-minute research task, the agent resumes from the last checkpoint instead of starting over. |

### Example in a RAG Agent

| Step                                 | LangGraph Feature   |
| ------------------------------------ | ------------------- |
| Retrieve documents                   | Persistent State    |
| Not enough evidence? Search again    | Cycles and Loops    |
| Choose Search / Summarize / Ask User | Conditional Routing |
| Server restarts during execution     | Crash Recovery      |

### Why this matters

Traditional **LangChain Chains** are generally:

```
A → B → C → End
```

LangGraph enables:

```mermaid
flowchart LR

    %% Runtime Components
    State[("📚 Persistent State")]
    Store[("💾 Checkpoint Store")]

    %% Workflow
    subgraph Workflow
        direction TB

        S1["Step 1<br/>🔍 Search"]

        S2{"Step 2<br/>Enough<br/>Evidence?"}

        S3["Step 3<br/>💬 Generate Answer"]

        S1 --> S2
        S2 -- Yes --> S3
        S2 -- No --> S1
    end

    %% Runtime
    State -. "Shared State" .-> S1
    State -. "Shared State" .-> S2
    State -. "Shared State" .-> S3

    S1 -. "Step 4<br/>Save State" .-> Store
    S2 -. "Step 4<br/>Save State" .-> Store
    S3 -. "Step 4<br/>Save State" .-> Store

    Store -. "Step 5<br/>Resume After Crash" .-> S1

    %% Styles
    style Workflow fill:none,stroke:#BDBDBD,stroke-width:2px

    style S1 fill:#42A5F5,color:#fff
    style S2 fill:#FFB74D,color:#000
    style S3 fill:#66BB6A,color:#fff

    style State fill:#EDE7F6,stroke:#7E57C2,stroke-width:2px
    style Store fill:#FFF8E1,stroke:#F9A825,stroke-width:2px
```

## When to use LangGraph

| Use LangChain When | Use LangGraph When |
|--------------------|--------------------|
| Simple chains | Stateful workflows |
| One-shot Q&A | Multi-turn agents |
| RAG pipelines | Self-correcting loops |
| No loops needed | Human-in-the-loop |
| Prototype phase | Production agents |

### Rule of Thumb

| If your application...                                    | Choose        |
| --------------------------------------------------------- | ------------- |
| Is a **linear** pipeline with no branching                    | **LangChain** |
| Requires **agentic workflows** with loops, memory, or conditional routing            | **LangGraph** |
| Needs **human approval** during execution                     | **LangGraph** |
| Is a simple chatbot or RAG demo                           | **LangChain** |
| Is a **production** AI agent with **multiple tools** and recovery | **LangGraph** |

> Simple guideline: LangChain is ideal for **linear** LLM applications, while LangGraph is designed for **stateful**, **agentic workflows** with loops, memory, conditional routing, and resilience.

---

## LangGraph Real-World Use Cases

| Use Case | Description |
|----------|-------------|
| **Customer Support Bot** | Handles customer tickets, escalates complex issues, and follows up with users. |
| **Research Agent** | Searches, evaluates, and iterates until sufficient evidence is found. |
| **Code Review** | Analyzes code, suggests improvements, and re-checks after changes. |
| **Approval Workflows** | Supports multi-day business processes with human review and approval. |

---

### LangGraph Features Used
| Use Case             | Persistent State |   Loops  | Conditional Routing | Human-in-the-loop |
| -------------------- | :--------------: | :------: | :-----------------: | :---------------: |
| Customer Support Bot |         ✅        |     ✅    |          ✅          |         ✅         |
| Research Agent       |         ✅        |     ✅    |          ✅          |         ❌         |
| Code Review          |         ✅        |     ✅    |          ✅          |      Optional     |
| Approval Workflows   |         ✅        | Optional |          ✅          |         ✅         |

---

> Here is the Markdown version of the slide:

```markdown
# Real-World Use Cases

| Use Case | Description |
|----------|-------------|
| **Customer Support Bot** | Handles customer tickets, escalates complex issues, and follows up with users. |
| **Research Agent** | Searches, evaluates, and iterates until sufficient evidence is found. |
| **Code Review** | Analyzes code, suggests improvements, and re-checks after changes. |
| **Approval Workflows** | Supports multi-day business processes with human review and approval. |
```

## Brief Explanation

| Use Case                 | Why LangGraph Fits                                                                                                         |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| **Customer Support Bot** | Maintains conversation history, routes requests, escalates to humans, and follows up automatically.                        |
| **Research Agent**       | Performs iterative searches, evaluates results, retries when needed, and stops only when sufficient evidence is collected. |
| **Code Review**          | Reviews code, suggests fixes, waits for updates, and re-runs analysis until quality criteria are met.                      |
| **Approval Workflows**   | Pauses execution for human approval, resumes later, and supports long-running business processes.                          |

## LangGraph Features Used

| Use Case             | Persistent State |   Loops  | Conditional Routing | Human-in-the-loop |
| -------------------- | :--------------: | :------: | :-----------------: | :---------------: |
| Customer Support Bot |         ✅        |     ✅    |          ✅          |         ✅         |
| Research Agent       |         ✅        |     ✅    |          ✅          |         ❌         |
| Code Review          |         ✅        |     ✅    |          ✅          |      Optional     |
| Approval Workflows   |         ✅        | Optional |          ✅          |         ✅         |

---

> **Key takeaway:** These use cases all involve more than a simple request-response interaction. They require **memory, iteration, decision-making, and often human intervention**, making them ideal candidates for **LangGraph** rather than a linear LangChain workflow.

---

## LangGraph 1.0 Highlights

| #     | Feature                  | Description                                                                                 | Why It Matters                                                                                         |
| ----- | ------------------------ | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **1** | **Durable State**        | Survives crashes and resumes execution from the last checkpoint.                            | Prevents losing progress during crashes or restarts, improving reliability for long-running workflows. |
| **2** | **Built-in Persistence** | Supports SQLite and PostgreSQL out of the box—no custom database code required.             | Reduces development effort while providing reliable, built-in state persistence.                       |
| **3** | **Human-in-the-Loop**    | Provides first-class interrupt and resume capabilities for human approval and intervention. | Enables safe collaboration between AI and humans for critical decisions and approvals.                 |
| **4** | **Production-Ready**     | Used in production by companies such as Uber, LinkedIn, and Klarna.                         | Delivers enterprise-grade reliability, scalability, and fault tolerance for production AI agents.      |



## Key Takeaway

> **LangGraph 1.0** is designed for **production AI agents**, offering:
>
> * ✅ Durable execution with automatic checkpointing
> * ✅ Built-in persistence (SQLite, PostgreSQL, etc.)
> * ✅ Human-in-the-loop workflows
> * ✅ Enterprise-ready reliability for long-running agent applications

---

## The Three Pilars


| #     | Pillar    | Description                                                        | LangGraph Example                                                     | Real-World Analogy                                                                                                                     |
| ----- | --------- | ------------------------------------------------------------------ | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | **State** | **What the agent knows and tracks** throughout execution.          | Chat history, user profile, retrieved documents, intermediate results | A patient's medical record that stores all relevant information.                                                                       |
| **2** | **Node**  | **Functions that process the state** by performing specific tasks. | Search documents, call GPT-5, execute a Python tool, summarize text   | A doctor examining the patient, making decisions, and updating the medical record.                                                     |
| **3** | **Edge**  | **Connections between nodes** that determine the execution flow.   | If confidence > 90%, generate the answer; otherwise, search again.    | The hospital workflow deciding whether the patient should receive treatment, undergo more tests, or be referred to another department. |

### Easy to Remember

| Pillar    | One Sentence                     |
| --------- | -------------------------------- |
| **State** | **Stores** what the agent knows. |
| **Node**  | **Processes** the information.   |
| **Edge**  | **Controls** what happens next.  |

> **Memory aid:**
> **State = Data**, **Node = Action**, **Edge = Flow**. These three pillars form the foundation of every LangGraph application.

---

```mermaid
flowchart LR

    State[(📚 State)]

    Search["🔍 Search"]

    Evaluate{"Enough Evidence?"}

    Tool["🛠️ Tool Call"]

    Reflect{"Reflection"}

    Answer["💬 Generate Answer"]

    %% Shared State
    State -. Read / Write .-> Search
    State -. Read / Write .-> Evaluate
    State -. Read / Write .-> Tool
    State -. Read / Write .-> Reflect
    State -. Read / Write .-> Answer

    %% Workflow
    Search --> Evaluate

    Evaluate -- No --> Search
    Evaluate -- Yes --> Tool

    Tool --> Reflect

    Reflect -- Retry --> Search
    Reflect -- Complete --> Answer
```

| 元件        | 簡單理解                   | 更精確的說明                                                            |
| --------- | ---------------------- | ----------------------------------------------------------------- |
| **Edge**  | **箭頭**                 | 定義 **下一個要執行哪個 Node**，可以是一般流程（Normal Edge）或條件流程（Conditional Edge）。 |
| **Node**  | **Process（處理程序）**      | 一個執行單元（通常是一個 Python function），負責讀取 State、執行工作，並更新 State。          |
| **State** | **共用狀態（Shared State）** | 所有 Node 共用的資料，任何 Node 都可以讀取（Read）和更新（Write）。                      |

---

##　StateGraph Explained

| Step  | Action           | What You Do                       | LangGraph Pillar        | Result                                                               |
| ----- | ---------------- | --------------------------------- | ----------------------- | -------------------------------------------------------------------- |
| **1** | **Define State** | Design the shared data structure. | **State**               | Every node can read from and update the same shared state.           |
| **2** | **Create Graph** | Instantiate a `StateGraph`.       | **Graph Container**     | Creates an empty workflow that will hold nodes and edges.            |
| **3** | **Add Nodes**    | Register processing functions.    | **Nodes**               | Defines the processing logic and capabilities of the AI agent.       |
| **4** | **Add Edges**    | Connect the nodes.                | **Edges**               | Defines the execution flow, routing, and transitions between nodes.  |
| **5** | **Compile**      | Build the executable graph.       | **Executable Workflow** | Produces a runnable LangGraph application ready to process requests. |


| Step  | Keyword     | Meaning                        |
| ----- | ----------- | ------------------------------ |
| **1** | **State**   | Define the shared data.        |
| **2** | **Graph**   | Create the workflow container. |
| **3** | **Nodes**   | Add processing logic.          |
| **4** | **Edges**   | Connect the workflow.          |
| **5** | **Compile** | Build and run the AI agent.    |

---

## State Definition

In LangGraph, the **State** defines the shared data that all nodes can read and update. Each field can specify how its value is updated during workflow execution.

| State Type | Definition | Update Behavior | Example |
|------------|------------|-----------------|---------|
| **Simple Field** | ```python current_step: str``` | Replaced each time | `old → new` |
| **Annotated (`add_messages`)** | ```python messages: Annotated[list, add_messages]``` | Appends new messages to the existing list | `[a] + [b] → [a, b]` |
| **Annotated (`operator.add`)** | ```python token_count: Annotated[int, operator.add]``` | Accumulates numeric values by addition | `5 + 3 → 8` |

> **Rule of Thumb**
>
> - **Simple Field** → Replace the previous value.
> - **`add_messages`** → Keep all conversation messages.
> - **`operator.add`** → Accumulate numeric values.

---

## Nodes

> Nodes receive full state, return partial updates

### INPUT: Full State
```python
state["messages"]
state["step_count"]
state["current_step"]
```

### PROCESS
- Read state
- Do work (LLM call, etc.)
- Return updates

### OUTPUT: Partial
```python
return {
  "messages": [resp],
  "current_step": "done"
}
```
---

## Edges

### Direct Edge
A always goes to B

```
A → B
```

```python
graph.add_edge("A", "B")
```

### Conditional Edge
A goes to B or C based on logic

```
A → B ?
A → C ?
```

```python
graph.add_conditional_edges(
  "A", routing_fn,
  {"route_b": "B", "route_c": "C"}
)
```

> routing_fn itself contains the conditional logic

## Hands on LangGraph

```bash
source .venv/Scripts/activate
cd langchain-course/

pyenv global 3.12.10
pyenv local 3.12.10

uv run langgraph_core.py
```

## Why Handoffs?

### What Is a Handoff?

A **handoff** transfers control of a request from one AI agent to another agent with more appropriate expertise.

Instead of requiring one general-purpose agent to handle every request, a **Triage Agent** analyzes the user's intent and delegates the task to a suitable specialist.

---

> The Real-World Problem *"Every company with a chatbot hits the same wall — one agent can't do everything."*

### Problem vs. Solution

| Problem | Solution |
|---|---|
| **Customer:** “I was charged twice.” | **Triage Agent → Billing Specialist** |
| A generic bot provides a vague answer, leaving the customer frustrated. | The request is routed to the appropriate specialist for faster and more accurate resolution. |

---

### The Problem: Generic Bot

```mermaid
flowchart LR

    C["Customer<br/>&quot;I was charged twice.&quot;"]
    G["Generic Bot"]
    R["Vague Answer<br/>Customer Frustrated"]

    C --> G
    G --> R

    style C fill:#E3F2FD,color:#000000,stroke:#1565C0,stroke-width:2px
    style G fill:#9E9E9E,color:#FFFFFF,stroke:#616161,stroke-width:2px
    style R fill:#FFCDD2,color:#000000,stroke:#C62828,stroke-width:2px
```

---

### The Solution: Agent Handoff

```mermaid
flowchart LR

    C["Customer Message<br/>&quot;I was charged twice.&quot;"]
    T{"Triage Agent<br/>Who should handle this?"}
    B["Billing Specialist"]
    R["Issue Resolved"]

    C --> T
    T -- "Billing Issue" --> B
    B --> R

    style C fill:#E3F2FD,color:#000000,stroke:#1565C0,stroke-width:2px
    style T fill:#9575CD,color:#FFFFFF,stroke:#512DA8,stroke-width:2px
    style B fill:#FFB74D,color:#000000,stroke:#EF6C00,stroke-width:2px
    style R fill:#81C784,color:#000000,stroke:#2E7D32,stroke-width:2px
```

---

### Multi-Agent Handoff Flow

```mermaid
flowchart TD

    M["Step 1<br/>Customer Message"]

    T{"Step 2 (Triage Agent)<br/>Who should handle?"}

    S["Step 3A<br/>Sales Agent"]
    P["Step 3B<br/>Support Agent"]
    B["Step 3C<br/>Billing Agent"]

    R["Step 4<br/>Final Response"]

    M --> T

    T -- "Sales Request" --> S
    T -- "Technical Issue" --> P
    T -- "Payment Issue" --> B

    S --> R
    P --> R
    B --> R

    style M fill:#616161,color:#FFFFFF,stroke:#424242,stroke-width:2px
    style T fill:#9575CD,color:#FFFFFF,stroke:#512DA8,stroke-width:2px
    style S fill:#42A5F5,color:#FFFFFF,stroke:#1565C0,stroke-width:2px
    style P fill:#66BB6A,color:#FFFFFF,stroke:#2E7D32,stroke-width:2px
    style B fill:#FFB74D,color:#000000,stroke:#EF6C00,stroke-width:2px
    style R fill:#26A69A,color:#FFFFFF,stroke:#00695C,stroke-width:2px
```

---

### Why Use Handoffs?

| Benefit | Description | Example |
|---|---|---|
| **Specialization** | Each agent focuses on a specific domain. | The Billing Agent handles invoices and payments. |
| **Better Accuracy** | A domain-specific agent can provide more precise answers. | The Support Agent diagnoses technical problems. |
| **Scalability** | New specialist agents can be added without redesigning the entire system. | Add AML or Trade Finance agents. |
| **Maintainability** | Each agent maintains its own prompts, tools, and business rules. | Update the Billing Agent without affecting Sales. |

---

### Enterprise Handoff Example

```mermaid
flowchart TD

    U["Customer Request"]
    T{"Triage Agent<br/>Classify Intent"}

    SALES["Sales Agent<br/>Plans and Upgrades"]
    SUPPORT["Support Agent<br/>Technical Issues"]
    BILLING["Billing Agent<br/>Payments and Refunds"]
    AML["AML Agent<br/>Suspicious Transactions"]
    TF["Trade Finance Agent<br/>LC and Documents"]

    U --> T

    T -- "Upgrade Plan" --> SALES
    T -- "Password Problem" --> SUPPORT
    T -- "Charged Twice" --> BILLING
    T -- "Suspicious Transaction" --> AML
    T -- "Review Letter of Credit" --> TF

    style U fill:#616161,color:#FFFFFF,stroke:#424242,stroke-width:2px
    style T fill:#9575CD,color:#FFFFFF,stroke:#512DA8,stroke-width:2px
    style SALES fill:#42A5F5,color:#FFFFFF,stroke:#1565C0,stroke-width:2px
    style SUPPORT fill:#66BB6A,color:#FFFFFF,stroke:#2E7D32,stroke-width:2px
    style BILLING fill:#FFB74D,color:#000000,stroke:#EF6C00,stroke-width:2px
    style AML fill:#EF5350,color:#FFFFFF,stroke:#B71C1C,stroke-width:2px
    style TF fill:#26A69A,color:#FFFFFF,stroke:#00695C,stroke-width:2px
```

---

### Furthermore - Handoff vs. Tool Call

| Handoff | Tool Call |
|---|---|
| Transfers control to another **AI agent**. | Invokes a **function, API, database, or external service**. |
| The specialist agent continues using its own prompt, tools, and expertise. | The same agent normally retains control after receiving the tool result. |
| Best suited to specialized reasoning and responsibility. | Best suited to performing a specific operation. |

```mermaid
flowchart LR

    A["Main Agent"]

    SA["Specialist Agent"]
    T["Tool / API"]

    A -- "Handoff<br/>Transfer Control" --> SA
    A -- "Tool Call<br/>Perform Operation" --> T
    T -- "Return Result" --> A

    style A fill:#9575CD,color:#FFFFFF,stroke:#512DA8,stroke-width:2px
    style SA fill:#FFB74D,color:#000000,stroke:#EF6C00,stroke-width:2px
    style T fill:#42A5F5,color:#FFFFFF,stroke:#1565C0,stroke-width:2px
```

> **Rule of thumb**
>
> - **Tool Call** = Ask a tool to perform a specific operation.
> - **Handoff** = Transfer the request to another specialist AI agent.


## Hands on Handsoff

```bash
uv run agent_handoffs.py
uv run agent_conversation.py
```
