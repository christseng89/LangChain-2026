# Chain Patterns

## The Pipe Operator Deep Dive

```note
chain = prompt | model | parser
```

Data flows left to right through each step:

| Step | Type | Method |
|------|------|--------|
| Input | `dict` | — |
| **prompt** | Runnable | `.invoke()` |
| **model** | Runnable | `.invoke()` |
| **parser** | Runnable | `.invoke()` |
| Output | `result` | — |

> **Key Concept**
>
> Each `|` creates a `RunnableSequence`. The chain itself is also a Runnable — composable all the way down.

## Chain Composition Patterns

### Sequential
`step1` → `step2` → `step3`

---

### Parallel (RunnableParallel)
`input` → `summarize_chain` → `{ summary: ..., keywords: ... }`
`.....` ↘ `keywords_chain`  ↗

---

### Passthrough (keep original) RAG
`question` --passes through--> `context` --from retriever--> `prompt | model | paser`

```python
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | parser
)
```

- `retriever` — takes the input `question` and fetches relevant `context` from the vector store
- `RunnablePassthrough()` — passes the original `question` through unchanged
- Both are bundled into a dict `{"context": ..., "question": ...}` which feeds into the `prompt`
- `prompt` — formats both into the final prompt template
- `model` — generates the response
- `parser` — structures the output

Here is the **Debugging Chains** slide converted to Markdown:

## Debugging Chains (Logging)

### 1. Verbose Logging
*Quick and simple* · **`Basic`**

Set `debug = True` to print all chain steps to console.

---

### 2. Callbacks
*Custom handlers* · **`Flexible`**

Attach callback handlers to intercept and log each step.

---

### 3. LangSmith
*Full tracing platform* · **`Recommended`**

Visual trace viewer, cost tracking, evaluation tools.

## 

```bash
source .venv/Scripts/activate
cd langchain-course/

pyenv global 3.12.10
pyenv local 3.12.10

uv run chains_v1.py
``