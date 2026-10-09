"""
Production-Ready FastAPI + LangGraph Application

Wires together:
- Security pipeline (input sanitization, PII masking)
- Response caching
- Rate limiting (slowapi)
- LangGraph agent (with retries + fallback)
- Structured logging + metrics
- LangSmith tracing
- Health checks
"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from langsmith import traceable
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.agent import ProductionAgent
from app.cache import ResponseCache
from app.common import print_section
from app.config import get_settings
from app.models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    MetricsResponse,
)
from app.monitoring import MetricsCollector, RequestTimer, get_logger
from app.security import SecurityPipeline

load_dotenv()
print_section("Starting Production API")


# === Global instances (initialized in lifespan) ===
security: SecurityPipeline = None
cache: ResponseCache = None
metrics: MetricsCollector = None
agent: ProductionAgent = None
logger = get_logger()


# === Lifespan (FastAPI startup/shutdown) ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize all components on startup, clean up on shutdown.
    This is the modern FastAPI pattern (replaces @app.on_event).
    """
    global security, cache, metrics, agent

    settings = get_settings()
    logger.info(
        "Starting production API...",
        extra={
            "extra_data": {
                "environment": settings.app_env,
                "project": settings.langsmith_project,
                "primary_model": settings.primary_model,
                "fallback_model": settings.fallback_model,
                "tracing_enabled": settings.langsmith_tracing,
            }
        },
    )

    # Initialize components
    security = SecurityPipeline()
    cache = ResponseCache(ttl_seconds=settings.cache_ttl_seconds)
    metrics = MetricsCollector()
    agent = ProductionAgent()

    logger.info("All components initialized. Ready to serve requests.")

    yield  # App is running

    # Shutdown
    print_section("Shutting down Production API")
    logger.info("Shutting down...", extra={"extra_data": metrics.summary})


# === Rate Limiter Setup ===
# 从 request 中取出客户端 IP,作为限流的计数键,所以每个 IP 单独计数。
limiter = Limiter(key_func=get_remote_address)

# === FastAPI App ===
app = FastAPI(
    title="Production LangGraph API",
    description="A production-ready chat API with security, caching, and observability.",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter


# === Exception Handlers ===
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    logger.warning(
        "Rate limit exceeded",
        extra={
            "extra_data": {
                "client_ip": get_remote_address(request),
            }
        },
    )
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": "Too many requests. Please slow down.",
        },
    )


# =============================================
# /chat PIPELINE STEPS
# =============================================
def _log_extra(**data) -> dict:
    """Wrap structured fields in the shape the JSON logger expects."""
    return {"extra_data": data}


# Step 1: Input sanitization and security checks
def _check_security(message: str, thread_id: str) -> tuple[str, list[str]]:
    """Step 1: sanitize input. Raises HTTP 400 if blocked."""
    is_allowed, cleaned_message, notes = security.check_input(message)

    if not is_allowed:
        logger.warning(
            "Request blocked by security",
            extra=_log_extra(reason=notes, thread_id=thread_id),
        )
        metrics.record_request(latency_ms=0, error=True, error_type="security_blocked")
        raise HTTPException(
            status_code=400,
            detail="Your message was blocked by our security filters.",
        )

    return cleaned_message, list(notes)


# Step 2: Cache lookup
def _cache_key(message: str, thread_id: str) -> str:
    """Cache entries are scoped per thread so conversations never share answers."""
    return f"{thread_id}\x00{message}"


def _cacheable(thread_id: str) -> bool:
    """Only first messages are cacheable: later answers depend on chat history."""
    return not agent.has_chat_history(thread_id)


def _cached_lookup(message: str, thread_id: str) -> ChatResponse | None:
    """Step 2: return a ChatResponse on cache hit, else None."""
    cached_response = cache.get(_cache_key(message, thread_id))
    if cached_response is None:
        return None

    metrics.record_request(latency_ms=0, cache_hit=True)
    logger.info("Cache hit", extra=_log_extra(thread_id=thread_id))
    return ChatResponse(
        response=cached_response,
        thread_id=thread_id,
        model_used="cache",
        cached=True,
        processing_time_ms=0,
    )


# Step 3: Invoke the LangGraph agent
def _invoke_agent(message: str, thread_id: str) -> dict:
    """Step 3: run the LangGraph agent. Raises HTTP 500 on failure."""
    try:
        return agent.invoke(message, thread_id)
    except Exception as e:
        logger.error(
            f"Agent invocation failed: {e}",
            extra=_log_extra(thread_id=thread_id, error=str(e)),
        )
        metrics.record_request(latency_ms=0, error=True, error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request.",
        )


# Step 6: Record metrics and log completion
def _record_metrics(
    *,
    thread_id: str,
    cleaned_message: str,
    response_text: str,
    model_used: str,
    latency_ms: float,
    security_notes: list[str],
) -> None:
    """Step 6: record metrics and emit completion logs."""
    metrics.record_request(
        latency_ms=latency_ms,
        input_tokens=int(len(cleaned_message.split()) * 1.3),
        output_tokens=int(len(response_text.split()) * 1.3),
        cache_hit=False,
        model=model_used,
    )

    if security_notes:
        logger.info(
            "Security notes",
            extra=_log_extra(notes=security_notes, thread_id=thread_id),
        )

    logger.info(
        "Request completed",
        extra=_log_extra(
            thread_id=thread_id,
            model_used=model_used,
            latency_ms=round(latency_ms, 2),
        ),
    )


# =============================================
# API ENDPOINTS
# =============================================
@app.post("/chat", response_model=ChatResponse)
@limiter.limit(get_settings().rate_limit)
@traceable(name="chat_endpoint")
async def chat(request: Request, body: ChatRequest):
    """
    Main chat endpoint.

    Flow:
    1. Security check (injection + PII masking)
    2. Cache lookup
    3. LangGraph agent invoke (if cache miss)
    4. Output validation
    5. Cache store
    6. Record metrics, log, return response
    """
    with RequestTimer() as timer:
        cleaned_message, security_notes = _check_security(body.message, body.thread_id)

        use_cache = _cacheable(body.thread_id)
        if use_cache and (
            reply := _cached_lookup(cleaned_message, body.thread_id)
        ) is not None:
            return reply

        result = _invoke_agent(cleaned_message, body.thread_id)
        model_used = result["model_used"]

        # Step 4: Output validation
        validated_response, output_warnings = security.check_output(result["response"])
        security_notes.extend(output_warnings)

        # Step 5: Cache the validated response
        if use_cache:
            cache.set(_cache_key(cleaned_message, body.thread_id), validated_response)

    _record_metrics(
        thread_id=body.thread_id,
        cleaned_message=cleaned_message,
        response_text=validated_response,
        model_used=model_used,
        latency_ms=timer.elapsed_ms,
        security_notes=security_notes,
    )

    return ChatResponse(
        response=validated_response,
        thread_id=body.thread_id,
        model_used=model_used,
        cached=False,
        processing_time_ms=round(timer.elapsed_ms, 2),
        security_notes=security_notes,
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check for Docker/Kubernetes."""
    settings = get_settings()

    checks = {
        "agent": agent is not None,
        "security": security is not None,
        "cache": cache is not None,
    }

    all_healthy = all(checks.values())

    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        environment=settings.app_env,
        checks=checks,
    )


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Metrics for monitoring dashboards."""
    summary = metrics.summary
    return MetricsResponse(**summary)


@app.get("/cache/stats")
async def cache_stats():
    """Cache performance statistics."""
    return cache.stats
