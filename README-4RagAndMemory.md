# RAG and Memory

## RAG Architecture

```mermaid
flowchart TD
    A["User Query<br/><small>input question</small>"]:::gray --> B["Retriever<br/><small>finds relevant docs</small>"]:::blue
    B --> C["Context + Query<br/><small>combined prompt</small>"]:::purple
    C --> D["LLM<br/><small>generates answer</small>"]:::green
    D --> E["Response<br/><small>grounded in docs</small>"]:::brown
    V["Vector Store<br/><small>Embedded documents<br/>Indexed for search</small>"]:::vectorstore -.-> B

    classDef gray fill:#9B9B9B,stroke:#7a7a7a,color:#fff,font-weight:bold
    classDef blue fill:#4A7A9D,stroke:#3a6280,color:#fff,font-weight:bold
    classDef purple fill:#7B5EA7,stroke:#654a8a,color:#fff,font-weight:bold
    classDef green fill:#3F8F5F,stroke:#337a4d,color:#fff,font-weight:bold
    classDef brown fill:#B5651D,stroke:#94530f,color:#fff,font-weight:bold
    classDef vectorstore fill:#ffffff,stroke:#2f6690,stroke-width:2px,color:#2f6690
```

> **Key Concept:** RAG grounds LLM responses in actual documents, reducing hallucination.

> The flow: `User Query → Retriever → Context + Query → LLM → Response`, with the **Retriever** pulling from a **Vector Store** of embedded, indexed documents on the side.

---

## Basic RAG Chain

**Diagram 1 – Chain Structure**
```mermaid
flowchart LR
    subgraph Chain["Chain Structure"]
        direction LR
        A["{ context, question }<br/><small>parallel inputs</small>"]:::gray --> B["prompt<br/><small>template</small>"]:::purple --> C["llm<br/><small>model</small>"]:::green --> D["parser<br/><small>output</small>"]:::brown
    end

    classDef gray fill:#9B9B9B,stroke:#7a7a7a,color:#fff,font-weight:bold
    classDef purple fill:#7B5EA7,stroke:#654a8a,color:#fff,font-weight:bold
    classDef green fill:#3F8F5F,stroke:#337a4d,color:#fff,font-weight:bold
    classDef brown fill:#B5651D,stroke:#94530f,color:#fff,font-weight:bold
```

**Diagram 2 – Prompt Template & Parallel Input Processing**
```mermaid
flowchart TD
    subgraph Prompt["Prompt Template"]
        PT["Answer based only on:<br/><br/>{context}<br/><br/>Question: {question}"]:::prompttext
    end

    subgraph Parallel["Parallel Input Processing"]
        R["retriever"]:::retriever --> CTX["context"]:::blue
        RP["RunnablePassthrough"]:::passthrough --> Q["question"]:::purple2
    end

    classDef blue fill:#4A7A9D,stroke:#3a6280,color:#fff,font-weight:bold
    classDef purple2 fill:#7B6BA0,stroke:#655388,color:#fff,font-weight:bold
    classDef retriever fill:#DCEBF7,stroke:#4A7A9D,color:#2f6690
    classDef passthrough fill:#EDE6F5,stroke:#7B5EA7,color:#5b4680
    classDef prompttext fill:#F3EEFB,stroke:#7B5EA7,color:#333
```

**Notes from the diagram:**
- `context` pulls from the **retriever**, while `question` passes straight through via **RunnablePassthrough** ("Question passes through unchanged").
- The prompt template combines them: *"Answer based only on: {context} — Question: {question}"*.
- Overall chain: `{context, question} → prompt → llm → parser`.

---

## Handling "I Don't Know"


```mermaid
flowchart LR

    subgraph With["✅ With Instruction"]
        direction LR
        Q2["Q:<br/>What is quantum<br/>computing?"]:::question
        A2["A:<br/>I <b>don't</b> have information<br/>about that in the<br/>provided context."]:::correct
        Q2 --> A2
    end

    subgraph Without["❌ Without Instruction"]
        direction LR
        Q1["Q:<br/>What is quantum<br/>computing?"]:::question
        A1["A:<br/>Quantum computing<br/>uses qubits...<br/><br/>(makes up answer)"]:::wrong
        Q1 --> A1
    end

    classDef question fill:#e8e8e8,stroke:#bbbbbb,color:#333,padding:18px
    classDef wrong fill:#fbdada,stroke:#c0392b,color:#c0392b,padding:18px
    classDef correct fill:#dcefdf,stroke:#2e7d4f,color:#2e7d4f,padding:18px

    style With fill:#ffffff,stroke:#2e7d4f,color:#2e7d4f
    style Without fill:#ffffff,stroke:#c0392b,color:#c0392b
```

```mermaid
flowchart TD

    subgraph Pattern["The Prompt Pattern"]

        P["Answer based <b>ONLY</b> on the following context.<br/><br/>If the <b>context doesn't</b> contain the answer, say <b>'I don't have information about that.'</b><br/>────────────────────────<br/>Context: {context}<br/>Question: {question}"]:::prompt

    end

    classDef prompt fill:#e8e0f2,stroke:#6c4f8c,color:#333,padding:24px

    style Pattern fill:#ffffff,stroke:#6c4f8c,color:#6c4f8c
```

> **Summary:** Without an explicit instruction, the LLM hallucinates an answer even when it lacks the information. Adding an instruction to the prompt ("say *I don't have information about that*") makes the model admit uncertainty instead of fabricating a response. This is achieved through a prompt pattern that constrains the answer strictly to the given context.

---

## RAG with Sources


```mermaid
flowchart LR

    subgraph Retriever["Retriever Output"]
        direction TD
        D1["Page content here...<br/><small>source: doc.pdf</small>"]
        D2["More content...<br/><small>source: guide.txt</small>"]
        D3["FAQ content...<br/><small>source: faq.md</small>"]

        D1 ~~~ D2
        D2 ~~~ D3

    end

    F["format_docs_with_sources<br/><small>Adds source tags to each chunk</small>"]:::formatter

    subgraph Formatted["Formatted Context"]
        C["[Source: doc.pdf]<br/>Page content...<br/><br/>[Source: guide.txt]<br/>More content...<br/><br/>[Source: faq.md]<br/>FAQ content..."]
    end

    Retriever --> F --> Formatted

    classDef formatter fill:#8a7ca8,stroke:#6c5a8c,color:#fff,font-weight:bold

    style Retriever fill:#ffffff,stroke:#4A7A9D,color:#4A7A9D
    style Formatted fill:#ffffff,stroke:#2e7d4f,color:#2e7d4f
```


> **Summary:** The `retriever` returns raw document chunks, each tagged with its source. The `format_docs_with_sources` function processes these chunks and attaches a `[Source: ...]` tag to each one, producing a formatted context block that preserves traceability back to the original documents.

> Users can verify answers.  Enable citation in responses. Builds trust. 使用者可驗證回答來源，並在回應中顯示引用（Citation），提升答案的可信度。

```python
  rag_chain = (
    {
      "context": retriever | format_docs_with_sources,
      "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
  )
```
---

## Hands on Basic RAG

```bash
source .venv/Scripts/activate
cd langchain-course/

pyenv global 3.12.10
pyenv local 3.12.10

uv run rag_pipeline.py
```
