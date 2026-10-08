"""Unit tests for app.models (no server or API key needed)."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    HealthResponse,
    MetricsResponse,
)
from app.monitoring import MetricsCollector


class TestChatRequest:
    def test_default_thread_id(self):
        req = ChatRequest(message="hi")
        assert req.message == "hi"
        assert req.thread_id == "default"

    def test_custom_thread_id(self):
        assert ChatRequest(message="hi", thread_id="t1").thread_id == "t1"

    def test_message_required(self):
        with pytest.raises(ValidationError):
            ChatRequest()

    def test_empty_message_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_message_length_boundaries(self):
        assert len(ChatRequest(message="a" * 10000).message) == 10000
        with pytest.raises(ValidationError):
            ChatRequest(message="a" * 10001)

    def test_non_string_message_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message=123)


class TestChatResponse:
    def make(self, **overrides):
        data = dict(
            response="ok", thread_id="t1", model_used="gpt-4o-mini", processing_time_ms=12.5
        )
        data.update(overrides)
        return ChatResponse(**data)

    def test_defaults(self):
        r = self.make()
        assert r.cached is False
        assert r.security_notes == []

    def test_required_fields(self):
        for missing in ("response", "thread_id", "model_used", "processing_time_ms"):
            data = dict(
                response="ok", thread_id="t1", model_used="m", processing_time_ms=1.0
            )
            del data[missing]
            with pytest.raises(ValidationError):
                ChatResponse(**data)

    def test_timestamp_is_utc_iso(self):
        ts = datetime.fromisoformat(self.make().timestamp)
        assert ts.tzinfo is not None
        assert ts.utcoffset().total_seconds() == 0

    def test_security_notes_not_shared_between_instances(self):
        a, b = self.make(), self.make()
        a.security_notes.append("PII masked")
        assert b.security_notes == []

    def test_serialization_round_trip(self):
        r = self.make(cached=True, security_notes=["x"])
        assert ChatResponse(**r.model_dump()) == r


class TestHealthResponse:
    def test_defaults(self):
        h = HealthResponse(environment="development")
        assert h.status == "healthy"
        assert h.version == "1.1.0"
        assert h.checks == {}

    def test_environment_required(self):
        with pytest.raises(ValidationError):
            HealthResponse()

    def test_checks_not_shared_between_instances(self):
        a = HealthResponse(environment="x")
        a.checks["db"] = "ok"
        assert HealthResponse(environment="x").checks == {}


class TestMetricsResponse:
    REQUIRED = dict(
        total_requests=1,
        total_errors=0,
        error_rate="0.00%",
        avg_latency_ms=1.0,
        cache_hit_rate="0.00%",
        total_input_tokens=1,
        total_output_tokens=1,
    )

    def test_defaults(self):
        m = MetricsResponse(**self.REQUIRED)
        assert m.p50_latency_ms == 0.0
        assert m.p95_latency_ms == 0.0
        assert m.p99_latency_ms == 0.0
        assert m.max_latency_ms == 0.0
        assert m.requests_by_model == {}
        assert m.errors_by_type == {}

    def test_required_fields(self):
        for missing in self.REQUIRED:
            data = {k: v for k, v in self.REQUIRED.items() if k != missing}
            with pytest.raises(ValidationError):
                MetricsResponse(**data)

    def test_accepts_collector_summary(self):
        collector = MetricsCollector()
        collector.record_request(
            latency_ms=100, input_tokens=5, output_tokens=7, model="gpt-4o-mini"
        )
        collector.record_request(latency_ms=50, error=True, error_type="timeout")
        m = MetricsResponse(**collector.summary)
        assert m.total_requests == 2
        assert m.total_errors == 1
        assert m.requests_by_model == {"gpt-4o-mini": 1}
        assert m.errors_by_type == {"timeout": 1}

    def test_by_model_values_must_be_int(self):
        with pytest.raises(ValidationError):
            MetricsResponse(**self.REQUIRED, requests_by_model={"m": "many"})


class TestErrorResponse:
    def test_optional_fields_default_to_none(self):
        e = ErrorResponse(error="boom")
        assert e.detail is None
        assert e.request_id is None

    def test_error_required(self):
        with pytest.raises(ValidationError):
            ErrorResponse()

    def test_full(self):
        e = ErrorResponse(error="boom", detail="why", request_id="r1")
        assert e.model_dump() == {"error": "boom", "detail": "why", "request_id": "r1"}
