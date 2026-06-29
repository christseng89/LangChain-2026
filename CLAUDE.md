# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This repo contains two independent sub-projects, each with their own `.git` and `.venv`:

- **`langchain-course/`** — standalone Python scripts covering LangChain/LangGraph concepts (no server, no tests, just runnable demos)
- **`langchain-production-api/`** — production FastAPI + LangGraph application with security, caching, rate limiting, observability, and a test suite

---

## langchain-course

### Setup

```bash
# From repo root
cd langchain-course
uv venv
source .venv/Scripts/activate   # Windows Git Bash / PowerShell: .venv\Scripts\activate
uv pip install -r requirements.txt
```

Requires a `.env` file with `OPENAI_API_KEY` and optionally `ANTHROPIC_API_KEY` and LangSmith keys (`LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2`).

### Running scripts

Each `.py` file is a self-contained demo. Run any of them directly:

```bash
uv run langgraph_core.py
uv run rag_pipeline.py
uv run multi_agent_research_system.py
```

### Architecture

All scripts follow the same pattern: import LangChain/LangGraph primitives, define a `TypedDict` state schema, build a `StateGraph`, compile it, and call `.invoke()`. LangGraph graphs are the primary abstraction — nodes are plain Python functions, edges declare control flow, and state reducers (via `Annotated`) handle message accumulation.

The scripts progress from basics to advanced:
- `langgraph_core.py` → `StateGraph`, reducers, `add_messages`
- `conditional_edges.py`, `cycles_loops.py` → routing and loops
- `checkpointing.py`, `human_in_loop.py` → persistence and interrupts
- `supervisor_agent.py`, `hierarchical_agents.py`, `multi_agent_research_system.py` → multi-agent orchestration
- `rag_pipeline.py`, `advanced_rag.py`, `vector_stores.py` → RAG patterns

---

## langchain-production-api

### Setup

```bash
cd langchain-production-api
cp .env.example .env   # fill in OPENAI_API_KEY and LANGCHAIN_API_KEY
uv sync
```

### Running the server

```bash
uv run uvicorn app.main:app --reload --port 8000
```

API docs auto-generated at `http://localhost:8000/docs`.

### Running tests

```bash
# Unit tests (no server, no API key needed)
uv run pytest tests/test_security.py tests/test_cache.py -v

# All tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ -v --cov=app
```

### Docker

```bash
docker-compose up --build
```

### Architecture

The app is a FastAPI service wrapping a LangGraph agent. Every request passes through a fixed pipeline:

```
Request → SecurityPipeline → ResponseCache → ProductionAgent (LangGraph) → ResponseCache.set → Response
```

**`app/config.py`** — pydantic-settings `Settings` class, loaded once via `@lru_cache`. All configuration comes from environment variables; `get_settings()` is the single access point.

**`app/security.py`** — `SecurityPipeline` composes `InputSanitizer` (prompt injection detection) + `PIIDetector` (masking emails, phones, SSNs, card numbers) + `OutputValidator`. Inputs that match injection patterns are blocked (HTTP 400); PII is masked and passed through with a note.

**`app/cache.py`** — `ResponseCache` is an in-memory TTL cache (default 5 min). Cache keys are case-normalized message strings.

**`app/agent.py`** — `ProductionAgent` wraps a `StateGraph` with three nodes: `process` (primary model) → `fallback` (secondary model) → `error` (graceful message). Routing is conditional on whether `state["error"]` is set and `retry_count < max_retries`. The agent does not handle its own retries at the LLM call level (`max_retries=0` on the client); the graph topology is the retry mechanism.

**`app/monitoring.py`** — structured JSON logger (`get_logger()`) and `MetricsCollector` that tracks request counts, latency, token usage, cache hits, and errors. `RequestTimer` is a context manager for latency measurement.

**`app/main.py`** — FastAPI lifespan initializes all four global singletons (`security`, `cache`, `metrics`, `agent`). Rate limiting via `slowapi` is applied at the `/chat` endpoint. LangSmith tracing is applied via `@traceable` on both the endpoint and `ProductionAgent.invoke`.

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | required | LLM calls |
| `PRIMARY_MODEL` | `gpt-4o-mini` | Primary LLM |
| `FALLBACK_MODEL` | `gpt-4o-mini` | Fallback LLM |
| `LANGCHAIN_API_KEY` | `""` | LangSmith tracing |
| `LANGCHAIN_TRACING_V2` | `true` | Enable/disable tracing |
| `APP_ENV` | `development` | Affects logging behavior |
| `RATE_LIMIT` | `20/minute` | slowapi rate limit string |
| `CACHE_TTL_SECONDS` | `300` | Response cache TTL |
| `MAX_RETRIES` | `3` | Agent retry attempts |
