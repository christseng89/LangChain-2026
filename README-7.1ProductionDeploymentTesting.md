# LLM Testing Patterns

> Why Testing LLMs Is Different, Traditional software testing and LLM testing require different approaches because LLM applications produce **probabilistic outputs** rather than strictly deterministic results.

## Traditional Testing vs. LLM Testing

| Traditional Testing | → | LLM Testing |
|---|:---:|---|
| ✅ **Deterministic Outputs** | → | 🎲 **Probabilistic Outputs** |
| 🟰 **Exact Match Assertions** | → | ≈ **Semantic Evaluation** |
| ⚡ **Fast Execution** | → | ⏳ **Slow, Expensive** |
| 📦 **Isolated Units** | → | 🔗 **Complex Chains** |

---

# LLM Testing Strategies

LLM / Agent applications typically require multiple testing strategies because model outputs are **probabilistic** and workflows may involve multiple LLMs, Agents, Tools, and Prompts.

## Four Testing Strategies

| Testing Strategy | Main Purpose | Key Approach |
|---|---|---|
| 🧩 **Unit Tests** | Test individual components | **Mock LLM responses** |
| ✅ **Integration Tests** | Test the real integrated workflow | **Real LLM with evaluation metrics** |
| 🔄 **Regression Tests** | Detect quality or behavior degradation | **Detect prompt drift / behavior changes** |
| 🅰️🅱️ **A/B Tests** | Compare alternative implementations | **Compare prompt versions** |

---

## Testing Architecture

```mermaid
flowchart TD

    T["🧪 LLM Testing Strategies"]

    U["🧩 Unit Tests<br/>Mock LLM Responses"]
    I["✅ Integration Tests<br/>Real LLM + Eval Metrics"]
    R["🔄 Regression Tests<br/>Detect Prompt Drift"]
    AB["🅰️ / 🅱️ A/B Tests<br/>Compare Prompt Versions"]

    T --> U
    T --> I
    T --> R
    T --> AB

    style T fill:#172554,stroke:#60A5FA,stroke-width:4px,color:#FFFFFF

    style U fill:#164E63,stroke:#38BDF8,stroke-width:3px,color:#FFFFFF
    style I fill:#064E3B,stroke:#4ADE80,stroke-width:3px,color:#FFFFFF
    style R fill:#78350F,stroke:#FB923C,stroke-width:3px,color:#FFFFFF
    style AB fill:#4C1D95,stroke:#E879F9,stroke-width:3px,color:#FFFFFF
````

## 1. Unit Tests

> **Mock LLM responses**

測試單一 Function、Node、Agent 或其他 component，而不是每次都真正呼叫 LLM。

```text
Input
  ↓
Component / Node
  ↓
Mock LLM Response
  ↓
Assert Expected Behavior
```

主要優點：

* Fast
* Cheap
* Deterministic
* Suitable for CI/CD
* Easier to isolate failures

---

## 2. Integration Tests

> **Real LLM with evaluation metrics**

使用真正的 LLM 測試多個元件整合後的行為。

```text
Input
  ↓
Agent
  ↓
Real LLM
  ↓
Tools / RAG
  ↓
Output
  ↓
Evaluation Metrics
```

因為 LLM Output 不一定每次文字完全相同，所以通常不能只依賴 Exact Match，而需要評估：

* Correctness
* Relevance
* Faithfulness / Groundedness
* Completeness
* Safety

---

## 3. Regression Tests

> **Detect prompt drift**

當 Prompt、Model、Tools、RAG Data 或 Agent Workflow 改變後，確認原本正常的能力沒有退步。

```text
Baseline
   │
   ├── Prompt V1
   ├── Model V1
   └── Expected Quality
          ↓
       Change
          ↓
   Prompt / Model / Agent V2
          ↓
      Re-evaluate
          ↓
Regression?
```

核心問題：

> **新版是否讓原本好的結果變差？**

---

## 4. A/B Tests

> **Compare prompt versions**

比較兩種 Prompt、Model 或 Agent Strategy 的實際效果。

```text
             Test Dataset
                  │
          ┌───────┴───────┐
          ▼               ▼
     Version A        Version B
     Prompt A         Prompt B
          │               │
          ▼               ▼
      Eval Score       Eval Score
          └───────┬───────┘
                  ▼
             Compare
```

例如：

| Metric      |  Prompt A | Prompt B |
| ----------- | --------: | -------: |
| Correctness |      0.82 | **0.91** |
| Relevance   |      0.88 | **0.93** |
| Latency     |  **2.1s** |     2.8s |
| Cost        | **$0.02** |    $0.03 |

因此 A/B Testing 不一定只比較「誰回答比較好」，還可以同時比較：

**Quality + Latency + Token Usage + Cost**

---

## Key Takeaway

> **Unit Test** → Does each component work?

> **Integration Test** → Does the complete workflow work with a real LLM?

> **Regression Test** → Did the new version make anything worse?

> **A/B Test** → Which version performs better?

---

# Evaluation Metrics

LLM Evaluation 不能只看「答案是否完全一致」，而需要從多個品質維度評估模型輸出。

## Evaluation Metrics

| Metric | What It Measures | When to Use |
|---|---|---|
| 🎯 **Correctness** | **Is the answer right?** | Q&A, factual tasks |
| 🔗 **Relevance** | **Is it on-topic?** | RAG, retrieval |
| 🧩 **Coherence** | **Does it make sense?** | Generation |
| 👍 **Helpfulness** | **Is it useful?** | Assistants |
| 🛡️ **Harmlessness** | **Is it safe?** | All production apps |

---

## 1. Correctness — 答得對不對？

衡量答案在**事實、邏輯或預期結果上是否正確**。

```text
Question
   ↓
LLM Answer
   ↓
Compare with Ground Truth
   ↓
Correct?
````

**適合：**

* Q&A
* Factual Questions
* Calculation
* Business-rule questions

> **Correctness = Is the answer right?**

---

## 2. Relevance — 有沒有回答到問題？

衡量回答是否與使用者問題或檢索目標**直接相關**。

例如：

```text
Question:
"What is LangGraph Send API used for?"

Answer:
"Send supports dynamic task dispatch and fan-out."

→ High Relevance ✓
```

如果回答大量介紹 LangChain 歷史，但沒有回答 `Send`：

```text
→ Low Relevance ✗
```

**特別適合：RAG / Retrieval**

> **Relevance = Is it on-topic?**

---

## 3. Coherence — 回答是否通順、有邏輯？

即使每一句話單獨看都正確，整體也可能前後矛盾或沒有邏輯。

衡量：

* Logical flow
* Internal consistency
* Readability
* Structure
* Whether the answer makes sense as a whole

> **Coherence = Does it make sense?**

---

## 4. Helpfulness — 對使用者有沒有用？

答案可能：

```text
Correct ✓
Relevant ✓
Coherent ✓
```

但仍然可能：

```text
Too vague
Missing actionable details
Doesn't solve user's problem

→ Not Helpful ✗
```

因此 Helpfulness 更關心：

> **這個答案實際上是否幫助使用者完成目標？**

**特別適合：AI Assistants / Agents**

---

## 5. Harmlessness — 是否安全？

衡量模型輸出是否造成不必要的安全或內容風險。

例如：

* Unsafe content
* Harmful instructions
* Privacy / PII leakage
* Inappropriate content
* Policy violations

**適合所有 Production LLM Applications。**

> **Harmlessness = Is it safe?**

---

## Evaluation Model

```mermaid
flowchart LR

    O["🤖 LLM Output"]

    C["🎯 Correctness<br/>Is it right?"]
    R["🔗 Relevance<br/>Is it on-topic?"]
    CO["🧩 Coherence<br/>Does it make sense?"]
    H["👍 Helpfulness<br/>Is it useful?"]
    S["🛡️ Harmlessness<br/>Is it safe?"]

    E["⭐ Overall<br/>Quality"]

    O --> C
    O --> R
    O --> CO
    O --> H
    O --> S

    C --> E
    R --> E
    CO --> E
    H --> E
    S --> E

    style O fill:#172554,stroke:#60A5FA,stroke-width:4px,color:#FFFFFF
    style C fill:#064E3B,stroke:#4ADE80,stroke-width:3px,color:#FFFFFF
    style R fill:#164E63,stroke:#22D3EE,stroke-width:3px,color:#FFFFFF
    style CO fill:#4C1D95,stroke:#C4B5FD,stroke-width:3px,color:#FFFFFF
    style H fill:#78350F,stroke:#FBBF24,stroke-width:3px,color:#FFFFFF
    style S fill:#450A0A,stroke:#F87171,stroke-width:3px,color:#FFFFFF
    style E fill:#14532D,stroke:#34D399,stroke-width:4px,color:#FFFFFF
```

## Easy Way to Remember

> **Correctness** → 對不對？

> **Relevance** → 有沒有答到題？

> **Coherence** → 通不通順、有沒有邏輯？

> **Helpfulness** → 有沒有實際幫助？

> **Harmlessness** → 安不安全？


---

# Hands On Test Patterns

```bash
uv run testing_patterns.py 
```

> LangSmith -> Datasets & Experiments > qa-eval-dataset

---

```bash
uv run testing_patterns1_testCases.py
uv run testing_patterns2_prodDataset.py
```

| 对比项 | v1（Step 2） | v2（Step 3） |
|---|---|---|
| 所在函数 | `run_evaluation()` | `run_comparison()` |
| 使用的链 | 模块级 `v1_chain = prompt \| LLM` | 函数内新建 `v2_chain = detailed_prompt \| LLM` |
| Prompt 内容 | `"Answer this question concisely: {question}"`（简单版） | 更详细的指令:要求精确、事实类问题要准确、数学题只给答案 |
| 目标函数 | `qa_target_v1` | `qa_target_v2`（函数内嵌套定义） |
| `@traceable` 名称 | `"qa_target_v1"` | `"qa_target_v2"` |
| `experiment_prefix` | `"qa-chain-v1"` | `"qa-chain-v2"` |
| 使用的数据集 | `qa-eval-dataset`（相同） | `qa-eval-dataset`（相同） |
| 评估器 | `correctness`、`helpfulness`、`contains_answer`（相同） | `correctness`、`helpfulness`、`contains_answer`（相同） |
| `max_concurrency` | `2`（相同） | `2`（相同） |
| 结果打印标签 | `print_results(results, "v1")` | `print_results(results, "v2")` |
| 作用/目的 | 建立基线(baseline)评测结果 | 换了 prompt 后重新跑一遍,用来和 v1 在 LangSmith 面板里做 Compare Experiments |

**核心结论**:两次调用的评测框架(数据集、评估器、并发数)完全相同,唯一的自变量是 **prompt 和对应的链**——v2 想验证的是"更详细的 prompt 指令是否能提升回答质量"。`experiment_prefix` 不同只是为了在 LangSmith 里把两次实验分开标记,方便对比。

---

# The Testing Pyramid for LLM Applications

## Testing Pyramid for LLM Applications

| Frequency | Testing Level | Purpose | When to Run |
|---|---|---|---|
| 🟪 **Least Frequent** | **LangSmith Datasets** | Persistent, versioned evaluation datasets | **Weekly / Before deploy** |
| 🟧 ↓ | **Regression Tests** | Detect LLM/application quality drift | **Nightly** |
| 🟦 ↓ | **Integration Tests** | Test with a real LLM and perform keyword/response checks | **Before deploy** |
| 🟩 **Most Frequent** | **Unit Tests (Mocks)** | Free, fast; test your own code; no API calls needed | **Every commit** |

### Core Concept

**Least Frequent / Higher Cost**
  
🟪 LangSmith Datasets  
↓  
🟧 Regression Tests  
↓  
🟦 Integration Tests  
↓  
🟩 Unit Tests (Mocks)

**Most Frequent / Lower Cost**

核心概念就是：**越往下越便宜、越快、越頻繁；越往上越接近真實 LLM 品質驗證，但成本較高、執行頻率較低。**

---
