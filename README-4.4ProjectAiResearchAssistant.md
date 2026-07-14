# Project - AI Research Assitance

## Architecture

```mermaid
flowchart TD

    Q["User Question<br/><i>'What does the paper say about attention mechanisms?'</i>"]

    Q --> M["Conversation Memory"]
    Q --> MQ["Multi-Query Retriever"]
    Q --> CC["Contextual Compression"]

    M --> VS["Vector Store (Chroma)<br/>Indexed Research Documents"]
    MQ --> VS
    CC --> VS

    VS --> LLM["GPT-4o-mini<br/>Generate Answer with Sources & Confidence"]

    style Q fill:#2563EB,color:#FFFFFF,stroke:#1E40AF,stroke-width:2px
    style M fill:#7C3AED,color:#FFFFFF,stroke:#5B21B6,stroke-width:2px
    style MQ fill:#0284C7,color:#FFFFFF,stroke:#0369A1,stroke-width:2px
    style CC fill:#D97706,color:#FFFFFF,stroke:#92400E,stroke-width:2px
    style VS fill:#E0F2FE,stroke:#0284C7,stroke-width:2px
    style LLM fill:#16A34A,color:#FFFFFF,stroke:#166534,stroke-width:2px
```

## Features Checklist (Complete Production Ready RAG Application)

```mermaid
flowchart TD

    A["📄 Document Ingestion\n(pdf, web, text)"]
    B["✂️ Smart Chunking + Metadata"]
    C["🗄️ Vector Store"]
    D["🔍 Multi-Query Retrieval"]
    E["🗜️ Contextual Compression"]

    M["🧠 Conversation Memory \nwith Sessions"]

    F["🤖 GPT-4o-mini"]

    G["📑 Structured Output"]
    H["💬 Follow-up Questions"]
    I["❓ I Don't Know"]

    A --> B --> C --> D --> E --> F

    M -. Context .-> F

    F --> G
    G --> H
    G --> I

    style A fill:#16A34A,color:#FFFFFF
    style B fill:#0284C7,color:#FFFFFF
    style C fill:#E0F2FE
    style D fill:#0284C7,color:#FFFFFF
    style E fill:#D97706,color:#FFFFFF
    style M fill:#7C3AED,color:#FFFFFF
    style F fill:#16A34A,color:#FFFFFF
    style G fill:#2563EB,color:#FFFFFF
    style H fill:#2563EB,color:#FFFFFF
    style I fill:#DC2626,color:#FFFFFF

```

## Key Design Decisions

| Area | Design Decision | Purpose |
|------|-----------------|---------|
| Chunking | `chunk_size=1000`, `chunk_overlap=200` | Preserve document context |
| Embedding | `text-embedding-3-small` | Convert document chunks and queries into vectors for semantic search |
| Vector Store | Persistent Chroma (`./research_db`) | Store embeddings and support similarity retrieval across restarts |
| Retrieval | Multi-Query → Similarity Search → Top 4 | Improve recall by searching from multiple query perspectives |
| Memory | Recent Context Window (Last 10 Messages) + Session-based Memory (In-Memory) | Maintain separate conversation context per session while limiting prompt size |
| Output | Answer + Sources + Confidence + Suggestions | Provide transparent and actionable responses |

## Hands on Project

```bash
source .venv/Scripts/activate
cd langchain-course/

pyenv global 3.12.10
pyenv local 3.12.10

uv run research_assistant.py
```

## Research Assistant Program Flow

```mermaid
flowchart TD

    D["Research Documents"] --> CH["Text Chunking"]
    CH --> DE["Document Embedding<br/>text-embedding-3-small"]
    DE --> VS["Persistent Chroma Vector Store"]

    Q["User Question"] --> MQ["Multi-Query Retriever"]
    MQ --> QE["Query Embedding<br/>text-embedding-3-small"]
    QE --> VS

    VS -->|"Top-4 Similar Chunks"| LLM["GPT-4o-mini"]
    Q --> LLM
    M["Session-based Memory<br/>Recent 10 Messages"] --> LLM

    LLM --> O["Answer + Sources<br/>Confidence + Suggestions"]

    style D fill:#2563EB,color:#FFFFFF,stroke:#1E40AF,stroke-width:2px
    style CH fill:#0284C7,color:#FFFFFF,stroke:#0369A1,stroke-width:2px
    style DE fill:#7C3AED,color:#FFFFFF,stroke:#5B21B6,stroke-width:2px
    style Q fill:#2563EB,color:#FFFFFF,stroke:#1E40AF,stroke-width:2px
    style MQ fill:#0284C7,color:#FFFFFF,stroke:#0369A1,stroke-width:2px
    style QE fill:#7C3AED,color:#FFFFFF,stroke:#5B21B6,stroke-width:2px
    style VS fill:#0F766E,color:#FFFFFF,stroke:#115E59,stroke-width:2px
    style M fill:#7C3AED,color:#FFFFFF,stroke:#5B21B6,stroke-width:2px
    style LLM fill:#16A34A,color:#FFFFFF,stroke:#166534,stroke-width:2px
    style O fill:#D97706,color:#FFFFFF,stroke:#92400E,stroke-width:2px
```
