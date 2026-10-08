"""
Tests for the caching layer.
Fast, deterministic, no external dependencies.
"""

import time
from types import SimpleNamespace

import pytest

from app import cache as cache_module
from app.cache import ResponseCache


class FakeClock:
    """Controllable replacement for the `time` module used by app.cache."""

    def __init__(self, now: float = 1000.0):
        self.now = now

    def time(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock(monkeypatch):
    fake = FakeClock()
    monkeypatch.setattr(cache_module, "time", SimpleNamespace(time=fake.time))
    return fake


class TestResponseCache:
    """Test the response cache."""

    def setup_method(self):
        self.cache = ResponseCache(ttl_seconds=2)

    def test_cache_miss_returns_none(self):
        assert self.cache.get("unknown query") is None

    def test_cache_hit_returns_response(self):
        self.cache.set("What is Python?", "A programming language.")
        result = self.cache.get("What is Python?")
        assert result == "A programming language."

    def test_case_insensitive_matching(self):
        self.cache.set("What is Python?", "A programming language.")
        result = self.cache.get("what is python?")
        assert result == "A programming language."

    def test_ttl_expiration(self):
        self.cache = ResponseCache(ttl_seconds=1)
        self.cache.set("query", "response")
        assert self.cache.get("query") == "response"
        time.sleep(1.5)
        assert self.cache.get("query") is None

    def test_stats_tracking(self):
        self.cache.get("miss1")
        self.cache.get("miss2")
        self.cache.set("hit", "value")
        self.cache.get("hit")

        stats = self.cache.stats
        assert stats["hits"] == 1
        assert stats["misses"] == 2
        assert stats["cached_entries"] == 1


class TestKeyNormalization:
    def setup_method(self):
        self.cache = ResponseCache()

    @pytest.mark.parametrize(
        "variant",
        ["hello world", "HELLO WORLD", "Hello World", "  hello world  ", "\thello world\n"],
    )
    def test_equivalent_queries_share_an_entry(self, variant):
        self.cache.set("Hello World", "answer")
        assert self.cache.get(variant) == "answer"

    @pytest.mark.parametrize("other", ["hello  world", "hello", "hello world!", "helloworld"])
    def test_different_queries_do_not_collide(self, other):
        self.cache.set("hello world", "answer")
        assert self.cache.get(other) is None

    def test_key_is_a_fixed_length_hash(self):
        key = self.cache._make_key("some secret user question")

        assert len(key) == 64
        assert "secret" not in key
        int(key, 16)  # valid hex

    def test_key_is_deterministic(self):
        assert self.cache._make_key("Q") == self.cache._make_key("q ")

    def test_unicode_queries(self):
        self.cache.set("你好,世界", "你好!")
        assert self.cache.get("你好,世界") == "你好!"
        assert self.cache.get("Straße") is None

    def test_empty_query_can_be_cached(self):
        self.cache.set("", "empty")
        assert self.cache.get("") == "empty"
        assert self.cache.get("   ") == "empty"  # whitespace normalizes to empty


class TestSetAndGet:
    def setup_method(self):
        self.cache = ResponseCache()

    def test_set_overwrites_existing_entry(self):
        self.cache.set("q", "old")
        self.cache.set("q", "new")

        assert self.cache.get("q") == "new"
        assert self.cache.stats["cached_entries"] == 1

    def test_overwrite_via_case_variant(self):
        self.cache.set("Q", "old")
        self.cache.set("q", "new")

        assert self.cache.get("Q") == "new"
        assert self.cache.stats["cached_entries"] == 1

    def test_entries_are_independent(self):
        self.cache.set("a", "1")
        self.cache.set("b", "2")

        assert self.cache.get("a") == "1"
        assert self.cache.get("b") == "2"
        assert self.cache.stats["cached_entries"] == 2

    def test_response_is_returned_verbatim(self):
        text = "  Line 1\n\nLine 2 – ünïcode 你好  "
        self.cache.set("q", text)

        assert self.cache.get("q") == text

    def test_empty_response_is_a_hit_not_a_miss(self):
        self.cache.set("q", "")

        assert self.cache.get("q") == ""
        assert self.cache.stats["hits"] == 1

    def test_instances_do_not_share_state(self):
        other = ResponseCache()
        self.cache.set("q", "a")

        assert other.get("q") is None


class TestTTL:
    def test_default_ttl_is_five_minutes(self):
        assert ResponseCache().ttl == 300

    def test_entry_valid_just_before_expiry(self, clock):
        cache = ResponseCache(ttl_seconds=10)
        cache.set("q", "r")
        clock.advance(9.99)

        assert cache.get("q") == "r"

    def test_entry_expires_exactly_at_ttl(self, clock):
        cache = ResponseCache(ttl_seconds=10)
        cache.set("q", "r")
        clock.advance(10)

        assert cache.get("q") is None

    def test_entry_expired_after_ttl(self, clock):
        cache = ResponseCache(ttl_seconds=10)
        cache.set("q", "r")
        clock.advance(11)

        assert cache.get("q") is None

    def test_expired_entry_is_removed_on_access(self, clock):
        cache = ResponseCache(ttl_seconds=10)
        cache.set("q", "r")
        clock.advance(11)
        cache.get("q")

        assert cache.stats["cached_entries"] == 0

    def test_expired_entry_lingers_until_accessed(self, clock):
        # Documents current behavior: there is no background sweep, so expired
        # entries still count in cached_entries until they are looked up.
        cache = ResponseCache(ttl_seconds=10)
        cache.set("q", "r")
        clock.advance(11)

        assert cache.stats["cached_entries"] == 1

    def test_expired_lookup_counts_as_miss(self, clock):
        cache = ResponseCache(ttl_seconds=10)
        cache.set("q", "r")
        clock.advance(11)
        cache.get("q")

        stats = cache.stats
        assert stats["hits"] == 0
        assert stats["misses"] == 1

    def test_hit_does_not_extend_ttl(self, clock):
        cache = ResponseCache(ttl_seconds=10)
        cache.set("q", "r")
        clock.advance(6)
        assert cache.get("q") == "r"
        clock.advance(6)  # 12s since set

        assert cache.get("q") is None

    def test_set_again_refreshes_ttl(self, clock):
        cache = ResponseCache(ttl_seconds=10)
        cache.set("q", "r1")
        clock.advance(8)
        cache.set("q", "r2")
        clock.advance(8)  # 16s since first set, 8s since second

        assert cache.get("q") == "r2"

    def test_entries_expire_independently(self, clock):
        cache = ResponseCache(ttl_seconds=10)
        cache.set("old", "1")
        clock.advance(6)
        cache.set("new", "2")
        clock.advance(6)  # old: 12s, new: 6s

        assert cache.get("old") is None
        assert cache.get("new") == "2"

    def test_can_be_set_again_after_expiry(self, clock):
        cache = ResponseCache(ttl_seconds=10)
        cache.set("q", "old")
        clock.advance(11)
        assert cache.get("q") is None
        cache.set("q", "new")

        assert cache.get("q") == "new"

    def test_zero_ttl_never_hits(self, clock):
        cache = ResponseCache(ttl_seconds=0)
        cache.set("q", "r")

        assert cache.get("q") is None


class TestStats:
    def setup_method(self):
        self.cache = ResponseCache()

    def test_empty_cache_stats(self):
        assert self.cache.stats == {
            "hits": 0,
            "misses": 0,
            "hit_rate": "0.0%",
            "cached_entries": 0,
        }

    def test_stats_keys(self):
        assert set(self.cache.stats) == {"hits", "misses", "hit_rate", "cached_entries"}

    def test_only_misses_gives_zero_hit_rate(self):
        self.cache.get("a")
        self.cache.get("b")

        assert self.cache.stats["hit_rate"] == "0.0%"

    def test_only_hits_gives_full_hit_rate(self):
        self.cache.set("q", "r")
        self.cache.get("q")
        self.cache.get("q")

        assert self.cache.stats["hit_rate"] == "100.0%"

    def test_half_hit_rate(self):
        self.cache.set("q", "r")
        self.cache.get("q")
        self.cache.get("other")

        assert self.cache.stats["hit_rate"] == "50.0%"

    def test_hit_rate_is_rounded_to_one_decimal(self):
        self.cache.set("q", "r")
        self.cache.get("q")
        self.cache.get("x")
        self.cache.get("y")

        assert self.cache.stats["hit_rate"] == "33.3%"

    def test_set_does_not_affect_hit_or_miss_counts(self):
        self.cache.set("a", "1")
        self.cache.set("b", "2")

        stats = self.cache.stats
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["cached_entries"] == 2

    def test_stats_is_a_snapshot(self):
        before = self.cache.stats
        self.cache.get("x")

        assert before["misses"] == 0
        assert self.cache.stats["misses"] == 1
