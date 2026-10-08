"""Unit tests for app.config (no server or real API key needed)."""

import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings

SETTING_ENV_VARS = [
    "OPENAI_API_KEY",
    "PRIMARY_MODEL",
    "FALLBACK_MODEL",
    "LANGSMITH_TRACING",
    "LANGSMITH_API_KEY",
    "LANGSMITH_PROJECT",
    "APP_ENV",
    "LOG_LEVEL",
    "RATE_LIMIT",
    "CACHE_TTL_SECONDS",
    "MAX_RETRIES",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Remove config env vars so tests don't depend on the local environment or .env."""
    for name in SETTING_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def make_settings(**overrides) -> Settings:
    # _env_file=None prevents the real .env from leaking into the test
    return Settings(_env_file=None, **overrides)


class TestDefaults:
    def test_defaults(self):
        s = make_settings(openai_api_key="sk-test")
        assert s.primary_model == "gpt-4o-mini"
        assert s.fallback_model == "gpt-4o-mini"
        assert s.langsmith_tracing is True
        assert s.langsmith_api_key == ""
        assert s.langsmith_project == "production-api"
        assert s.app_env == "development"
        assert s.log_level == "INFO"
        assert s.rate_limit == "20/minute"
        assert s.cache_ttl_seconds == 300
        assert s.max_retries == 3

    def test_openai_api_key_is_required(self):
        with pytest.raises(ValidationError):
            make_settings()


class TestEnvLoading:
    def test_reads_from_environment(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-env")
        monkeypatch.setenv("PRIMARY_MODEL", "gpt-4o")
        monkeypatch.setenv("RATE_LIMIT", "5/second")
        s = make_settings()
        assert s.openai_api_key == "sk-env"
        assert s.primary_model == "gpt-4o"
        assert s.rate_limit == "5/second"

    def test_numeric_values_are_coerced(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-env")
        monkeypatch.setenv("CACHE_TTL_SECONDS", "60")
        monkeypatch.setenv("MAX_RETRIES", "5")
        s = make_settings()
        assert s.cache_ttl_seconds == 60
        assert s.max_retries == 5

    def test_boolean_coercion(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-env")
        monkeypatch.setenv("LANGSMITH_TRACING", "false")
        assert make_settings().langsmith_tracing is False

    def test_invalid_int_raises(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-env")
        monkeypatch.setenv("MAX_RETRIES", "not-a-number")
        with pytest.raises(ValidationError):
            make_settings()

    def test_unknown_env_vars_are_ignored(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-env")
        monkeypatch.setenv("SOMETHING_UNRELATED", "x")
        s = make_settings()
        assert not hasattr(s, "something_unrelated")


class TestIsProduction:
    @pytest.mark.parametrize(
        "env,expected",
        [("production", True), ("development", False), ("staging", False), ("Production", False)],
    )
    def test_is_production(self, env, expected):
        s = make_settings(openai_api_key="sk-test", app_env=env)
        assert s.is_production is expected


class TestGetSettings:
    def test_is_cached(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-cached")
        assert get_settings() is get_settings()

    def test_cache_clear_reloads(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-one")
        first = get_settings()
        monkeypatch.setenv("OPENAI_API_KEY", "sk-two")
        assert get_settings().openai_api_key == "sk-one"
        get_settings.cache_clear()
        assert get_settings().openai_api_key == "sk-two"
        assert get_settings() is not first
