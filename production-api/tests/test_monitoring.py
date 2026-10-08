"""Unit tests for app.monitoring (no server or API key needed)."""

import json
import logging
import threading
import time

import pytest

from app.monitoring import JSONFormatter, MetricsCollector, RequestTimer, get_logger


def make_record(msg="hello", level=logging.INFO, **attrs) -> logging.LogRecord:
    record = logging.LogRecord(
        name="test", level=level, pathname=__file__, lineno=1,
        msg=msg, args=(), exc_info=None, func="test_func",
    )
    for key, value in attrs.items():
        setattr(record, key, value)
    return record


class TestJSONFormatter:
    def test_outputs_valid_json_with_base_fields(self):
        out = json.loads(JSONFormatter().format(make_record("hello")))
        assert out["message"] == "hello"
        assert out["level"] == "INFO"
        assert out["function"] == "test_func"
        assert out["module"] == "test_monitoring"
        assert "timestamp" in out

    def test_message_args_are_interpolated(self):
        record = make_record("user %s", )
        record.args = ("bob",)
        assert json.loads(JSONFormatter().format(record))["message"] == "user bob"

    def test_extra_data_is_merged(self):
        record = make_record(extra_data={"user_id": "u1", "count": 3})
        out = json.loads(JSONFormatter().format(record))
        assert out["user_id"] == "u1"
        assert out["count"] == 3

    def test_level_name_reflects_record(self):
        out = json.loads(JSONFormatter().format(make_record(level=logging.WARNING)))
        assert out["level"] == "WARNING"


class TestGetLogger:
    @pytest.fixture
    def logger_name(self):
        name = f"test-logger-{time.time_ns()}"
        yield name
        logger = logging.getLogger(name)
        logger.handlers.clear()

    def test_configures_json_handler_and_level(self, logger_name):
        logger = get_logger(logger_name)
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, JSONFormatter)

    def test_does_not_add_duplicate_handlers(self, logger_name):
        get_logger(logger_name)
        get_logger(logger_name)
        assert len(logging.getLogger(logger_name).handlers) == 1

    def test_returns_same_logger_instance(self, logger_name):
        assert get_logger(logger_name) is get_logger(logger_name)


class TestMetricsCollectorEmpty:
    def test_empty_summary(self):
        s = MetricsCollector().summary
        assert s["total_requests"] == 0
        assert s["total_errors"] == 0
        assert s["error_rate"] == "0.00%"
        assert s["cache_hit_rate"] == "0.00%"
        assert s["avg_latency_ms"] == 0.0
        assert s["p50_latency_ms"] == 0.0
        assert s["p95_latency_ms"] == 0.0
        assert s["p99_latency_ms"] == 0.0
        assert s["max_latency_ms"] == 0.0
        assert s["requests_by_model"] == {}
        assert s["errors_by_type"] == {}


class TestMetricsCollectorRecording:
    def test_counts_and_tokens(self):
        m = MetricsCollector()
        m.record_request(latency_ms=100, input_tokens=10, output_tokens=20)
        m.record_request(latency_ms=200, input_tokens=5, output_tokens=15)
        s = m.summary
        assert s["total_requests"] == 2
        assert s["total_input_tokens"] == 15
        assert s["total_output_tokens"] == 35
        assert s["avg_latency_ms"] == 150.0
        assert s["max_latency_ms"] == 200.0

    def test_error_rate_and_types(self):
        m = MetricsCollector()
        m.record_request(latency_ms=10)
        m.record_request(latency_ms=10, error=True, error_type="timeout")
        m.record_request(latency_ms=10, error=True, error_type="timeout")
        m.record_request(latency_ms=10, error=True)
        s = m.summary
        assert s["total_errors"] == 3
        assert s["error_rate"] == "75.00%"
        assert s["errors_by_type"] == {"timeout": 2, "unknown": 1}

    def test_error_type_ignored_when_not_error(self):
        m = MetricsCollector()
        m.record_request(latency_ms=10, error_type="timeout")
        assert m.summary["errors_by_type"] == {}

    def test_cache_hit_rate(self):
        m = MetricsCollector()
        m.record_request(latency_ms=1, cache_hit=True)
        m.record_request(latency_ms=1, cache_hit=False)
        m.record_request(latency_ms=1, cache_hit=False)
        m.record_request(latency_ms=1, cache_hit=True)
        assert m.summary["cache_hit_rate"] == "50.00%"

    def test_requests_by_model(self):
        m = MetricsCollector()
        m.record_request(latency_ms=1, model="gpt-4o")
        m.record_request(latency_ms=1, model="gpt-4o")
        m.record_request(latency_ms=1, model="gpt-4o-mini")
        m.record_request(latency_ms=1)  # no model -> not counted
        assert m.summary["requests_by_model"] == {"gpt-4o": 2, "gpt-4o-mini": 1}

    def test_summary_returns_copies(self):
        m = MetricsCollector()
        m.record_request(latency_ms=1, model="a")
        m.summary["requests_by_model"]["a"] = 99
        assert m.summary["requests_by_model"] == {"a": 1}


class TestPercentiles:
    def test_percentiles(self):
        m = MetricsCollector()
        for v in (50, 10, 40, 20, 30):  # unsorted on purpose
            m.record_request(latency_ms=v)
        s = m.summary
        assert s["p50_latency_ms"] == 30
        assert s["p95_latency_ms"] == 50
        assert s["p99_latency_ms"] == 50

    def test_zero_latency_excluded_from_percentiles_but_not_average(self):
        m = MetricsCollector()
        m.record_request(latency_ms=0)
        m.record_request(latency_ms=100)
        s = m.summary
        assert s["p50_latency_ms"] == 100
        assert s["avg_latency_ms"] == 50.0
        assert s["total_requests"] == 2

    def test_only_zero_latencies_give_zero_percentiles(self):
        m = MetricsCollector()
        m.record_request(latency_ms=0)
        assert m.summary["p99_latency_ms"] == 0.0

    def test_recent_window_is_bounded(self):
        m = MetricsCollector()
        # 1000 slow requests followed by 1000 fast ones: slow ones age out
        for _ in range(1000):
            m.record_request(latency_ms=1000)
        for _ in range(1000):
            m.record_request(latency_ms=1)
        s = m.summary
        assert s["p99_latency_ms"] == 1
        assert s["max_latency_ms"] == 1000  # max is all-time, not windowed

    def test_percentile_helper(self):
        assert MetricsCollector._percentile([], 50) == 0.0
        assert MetricsCollector._percentile([1.234], 99) == 1.23


class TestThreadSafety:
    def test_concurrent_recording(self):
        m = MetricsCollector()

        def work():
            for _ in range(500):
                m.record_request(latency_ms=1, input_tokens=1, model="x")

        threads = [threading.Thread(target=work) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        s = m.summary
        assert s["total_requests"] == 4000
        assert s["total_input_tokens"] == 4000
        assert s["requests_by_model"] == {"x": 4000}


class TestRequestTimer:
    def test_measures_elapsed_ms(self):
        with RequestTimer() as timer:
            time.sleep(0.05)
        assert 40 <= timer.elapsed_ms < 1000

    def test_elapsed_set_when_exception_raised(self):
        timer = RequestTimer()
        with pytest.raises(ValueError):
            with timer:
                raise ValueError("boom")
        assert timer.elapsed_ms >= 0
