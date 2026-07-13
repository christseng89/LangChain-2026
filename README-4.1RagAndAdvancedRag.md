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

> {{context}} 不要被 Python 解讀，而是保留給 LangChain。

---

## 🎯 Advanced RAG

### 🔴 Basic RAG Limitations

| #    | Limitation                         | Impact                          |
| ---- | ---------------------------------- | ------------------------------- |
| 🔴① | **Single query perspective** | → Misses relevant docs         |
| 🔴② | **No metadata filtering**    | → Retrieves irrelevant content |
| 🔴③ | **Full chunks returned**     | → Noise in context             |
| 🔴④ | **Keyword OR semantic**      | → Not both together            |

### 🟢 Advanced RAG Solutions

- 🟣 **Multi-Query Retriever** — Multiple perspectives

````markdown
    Query1 ─┐
    Query2 ─┼──► Vector Store
    Query3 ─┤
    Query4 ─┘
````

- 🔵 **Self-Query Retriever** — Auto metadata filters

````markdown
    Vector Search
    +
    Metadata Filter
````

- 🟠 **Contextual Compression** — Extract relevant parts

    > Chunk 大 + 相關資訊密度低 → compression 值得用（省下的 token/降低干擾 多付出的 LLM 呼叫成本）
    > Chunk 小 + 本來就很聚焦 → compression 通常不划算，純粹增加延遲和費用

```markdown

    - Token 少很多
    - 成本降低
    - 答案更精準
```

- 🟢 **Hybrid Search** — Keywords + semantic

````markdown
# Hybrid Search
                    User Query
                        │
            ┌─────────────┴─────────────┐
            ▼                           ▼
    Keyword Search (BM25)      Vector Search
    找完全匹配文字               找語意相近內容
            │                           │
            └─────────────┬─────────────┘
                        ▼
                Hybrid Ranking
                        ▼
        更完整、更精確的搜尋結果

> BM25: Best Matching 25, Elasticsearch、OpenSearch、Lucene 等搜尋引擎的預設排名演算法。

## Example

        User Query: 
        What fields are required in MT700?
                │
                ▼
        Retriever
        (Vector Search)
                │
                ▼
        Top-3 Retrieved Chunks

        1. Source: SWIFT MT700 Specification
        - Field 20
        - Field 40A
        - Field 31D

        2. Source: Import LC Product Manual
        - MT700 Generation

        3. Source: LC Issue User Guide
        - Issue Screen Mapping

````

| 技術                               | 解決什麼問題           | 實際例子                             |
| ---------------------------------- | ---------------------- | ------------------------------------ |
| 🟣**Multi-Query Retriever**  | 從不同角度搜尋         | 同一個問題產生多個 Query，提高召回率 |
| 🔵**Self-Query Retriever**   | 自動加 Metadata Filter | LLM 自動判斷要搜尋哪些文件           |
| 🟠**Contextual Compression** | 去除無關內容           | 只保留與問題相關的段落               |
| 🟢**Hybrid Search**          | Keyword + Semantic     | 同時利用關鍵字與向量搜尋             |

---

```markdown
# Advanced RAG Architecture

          User Question
               │
               ▼
┌─────────────────────────────┐
│ Multi-Query Retriever       │
│ 同一問題產生多個 Query       │
│ Via LLM                     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Self-Query Retriever        │
│ 自動加入 Metadata Filter     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Hybrid Search               │
│ Keyword + Vector Search     │
└──────────────┬──────────────┘
               │
               ▼
         Retrieved Documents
               │
               ▼
┌─────────────────────────────┐
│ Contextual Compression      │
│ 移除無關內容，只保留重點      │
└──────────────┬──────────────┘
               │
               ▼
              LLM

```

---

## 🟣 Multi-Query Retriever

```mermaid
flowchart TD

    Q["Original Query<br/>What are the benefits of exercise?"]:::query

    LLM["LLM<br/>Generate Query Variations"]:::llm

    Q --> LLM

    LLM --> Q1["Query 1<br/>How does physical activity improve health?"]:::variation
    LLM --> Q2["Query 2<br/>What positive effects does working out have?"]:::variation
    LLM --> Q3["Query 3<br/>Why should people exercise regularly?"]:::variation

    Q1 --> R1["Retriever<br/>Results 1"]:::result
    Q2 --> R2["Retriever<br/>Results 2"]:::result
    Q3 --> R3["Retriever<br/>Results 3"]:::result

    R1 --> M["Merge and Deduplicate"]:::merge
    R2 --> M
    R3 --> M

    M --> O["Unique Retrieved Chunks"]:::output

    classDef query fill:#f5f5f5,stroke:#aaaaaa,color:#333;
    classDef llm fill:#8a6fa8,stroke:#6c4f8c,color:#fff,font-weight:bold;
    classDef variation fill:#eee7f5,stroke:#8a6fa8,color:#333;
    classDef result fill:#eef8f1,stroke:#4f8f63,color:#2e7d4f;
    classDef merge fill:#4f8f63,stroke:#2e6e43,color:#fff,font-weight:bold;
    classDef output fill:#dff3df,stroke:#2e7d4f,color:#2e7d4f,font-weight:bold;
```

---

## ⚪ Self-Query Retriever

```mermaid
flowchart TD

    Q["User Query<br/><br/>Show Import LC manuals<br/>after 2024"]:::query

    LLM["LLM<br/>Parse Query"]:::llm

    Q --> LLM

    LLM --> SQ
    LLM --> MF

    subgraph SQ["Semantic Query"]
        direction TB
        S1["Import LC"]:::semantic
    end

    subgraph MF["Metadata Filter (Auto-generated)"]
        direction TB
        M1["module = Import LC<br/>year >= 2024<br/>doc_type = Manual"]:::metadata
    end

    SQ --> R
    MF --> R

    R["Retriever"]:::retriever

    R --> O["Top-K Retrieved Chunks"]:::output

    classDef query fill:#f5f5f5,stroke:#999,color:#333;
    classDef llm fill:#6b9fd4,stroke:#4c7fb5,color:#fff,font-weight:bold;
    classDef semantic fill:#eee7f5,stroke:#8a6fa8,color:#333;
    classDef metadata fill:#fdf3ea,stroke:#c98d5d,color:#8a5a32;
    classDef retriever fill:#4f8f63,stroke:#2e6e43,color:#fff,font-weight:bold;
    classDef output fill:#dff3df,stroke:#2e7d4f,color:#2e7d4f;

    style SQ fill:#ffffff,stroke:#8a6fa8
    style MF fill:#ffffff,stroke:#c98d5d
```
---

## MultiQueryRetriever vs SelfQueryRetriever

| 比較項目          | 🟣 MultiQueryRetriever | 🔵 SelfQueryRetriever           |
| ------------- | ---------------------- | ------------------------------- |
| 核心目的          | 提高 **Recall（召回率）**     | 提高 **Precision（精確率）**           |
| LLM 的工作       | 將一個問題改寫成多個 Query       | 解析問題並產生 Query + **Metadata Filter** |
| 解決問題          | 同一種問法可能找不到所有相關文件       | 文件太多，需要**縮小搜尋**範圍                   |
| 搜尋次數          | **多次**搜尋，再合併結果             | 通常**一次**搜尋，但加入 Filter               |
| 是否使用 Metadata | ❌ 不需要                  | ✅ 需要                            |

### 一句話總結
| Retriever                  | 核心概念                                                                              |
| -------------------------- | --------------------------------------------------------------------------------- |
| 🟣 **MultiQueryRetriever** | **Expand the Query**：將一個問題改寫成多個 Query，提高 **Recall**，避免漏掉相關文件。                     |
| 🔵 **SelfQueryRetriever**  | **Add Metadata Filters**：從問題中推論搜尋條件，自動加入 Metadata Filter，提高 **Precision**，縮小搜尋範圍。 |

---

## Context Compression Retrival

```mermaid
flowchart LR

    A["Top-K Retrieved Chunks<br/><br/>包含相關與不相關內容"]:::input

    B["Contextual Compressor<br/><br/>LLM / Embedding Filter / Re-ranker"]:::compressor

    C["Compressed Context<br/><br/>只保留與 Query 相關的段落"]:::output

    D["Final LLM<br/><br/>產生更精準的回答"]:::llm

    A --> B --> C --> D

    classDef input fill:#f5f5f5,stroke:#999999,color:#333;
    classDef compressor fill:#b98255,stroke:#8d603d,color:#ffffff,font-weight:bold;
    classDef output fill:#e6f4e8,stroke:#4f8f63,color:#2e7d4f;
    classDef llm fill:#e8e0f2,stroke:#6c4f8c,color:#333,font-weight:bold;
```

## Hybrid Search (BM25 + Semantic)

```mermaid
flowchart TD

    Q["User Query"]:::query

    Q --> BM25
    Q --> Vector

    subgraph BM25["BM25 Retriever"]
        direction TB
        B1["Keyword Matching 40%"]:::desc
        B2["Best for:<br/>Exact terms<br/>Names<br/>Codes"]:::bm25
    end

    subgraph Vector["Semantic Retriever"]
        direction TB
        V1["Vector Search 60%"]:::desc
        V2["Best for:<br/>Concepts<br/>Synonyms<br/>Meaning"]:::semantic
    end

    BM25 --> Merge
    Vector --> Merge

    Merge["Hybrid Ranking<br/>(EnsembleRetriever)"]:::ensemble

    Merge --> Docs["Top-K Retrieved Chunks"]:::output

    classDef query fill:#f5f5f5,stroke:#999,color:#333;
    classDef desc fill:#ffffff,stroke:#dddddd,color:#555;
    classDef bm25 fill:#c98d5d,stroke:#a66c3b,color:#fff;
    classDef semantic fill:#6b9fd4,stroke:#4c7fb5,color:#fff;
    classDef ensemble fill:#4f8f63,stroke:#2e6e43,color:#fff,font-weight:bold;
    classDef output fill:#dff3df,stroke:#2e7d4f,color:#2e7d4f;

    style BM25 fill:#ffffff,stroke:#c98d5d
    style Vector fill:#ffffff,stroke:#6b9fd4
```

## Parent Document Retriever

```mermaid
flowchart TD

    D["Original Document"]:::document

    D --> P["Parent Chunk<br/>1000 characters"]:::parent

    P --> C1["Child Chunk 1<br/>200 characters"]:::child
    P --> C2["Child Chunk 2<br/>200 characters"]:::child
    P --> C3["Child Chunk 3<br/>200 characters"]:::child
    P --> C4["Child Chunk 4<br/>200 characters"]:::child
    P --> C5["Child Chunk 5<br/>200 characters"]:::child

    Q["User Query"]:::query

    Q --> VS["Vector Search<br/>Search Small Child Chunks"]:::search

    C1 --> VS
    C2 --> VS
    C3 --> VS
    C4 --> VS
    C5 --> VS

    VS --> Match["Matched Child Chunk"]:::matched

    Match --> Lookup["Use Parent ID<br/>Lookup Parent Chunk"]:::lookup

    Lookup --> Context["Return Large Parent Chunk<br/>Full Context"]:::context

    Context --> LLM["LLM"]:::llm

    classDef document fill:#f5f5f5,stroke:#999,color:#333;
    classDef parent fill:#eee7f5,stroke:#8a6fa8,color:#6c4f8c,font-weight:bold;
    classDef child fill:#e6f4e8,stroke:#4f8f63,color:#2e7d4f;
    classDef query fill:#f5f5f5,stroke:#999,color:#333;
    classDef search fill:#4f8f63,stroke:#2e6e43,color:#fff,font-weight:bold;
    classDef matched fill:#dff3df,stroke:#2e7d4f,color:#2e7d4f;
    classDef lookup fill:#fdf3ea,stroke:#c98d5d,color:#8a5a32;
    classDef context fill:#eee7f5,stroke:#8a6fa8,color:#6c4f8c,font-weight:bold;
    classDef llm fill:#6b9fd4,stroke:#4c7fb5,color:#fff,font-weight:bold;
```

## Hands on Advanced RAG

```bash
source .venv/Scripts/activate
cd langchain-course/

pyenv global 3.12.10
pyenv local 3.12.10

uv run advanced_rag.py
```