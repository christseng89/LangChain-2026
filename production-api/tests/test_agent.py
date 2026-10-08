"""
Tests for app/agent.py (ProductionAgent).

No real LLM calls: ChatOpenAI is replaced with a scripted fake, and the
side-effecting helpers (print_llm_info, save_graph_png) are patched out.
Run with:
    uv run pytest tests/test_agent.py -v
"""

import os

# Must be set before app modules are imported (settings + tracing read the env)
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app import agent as agent_module
from app.agent import ProductionAgent

ERROR_MESSAGE = (
    "I'm sorry, I'm having trouble processing your request "
    "right now. Please try again in a moment."
)


class ScriptedLLM:
    """Fake chat model. Each call pops the next outcome: a string or an Exception."""

    def __init__(self, outcomes=None, **init_kwargs):
        self.outcomes = list(outcomes or [])
        self.init_kwargs = init_kwargs
        self.calls: list[list] = []

    def invoke(self, messages):
        self.calls.append(messages)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return AIMessage(content=outcome)


@pytest.fixture
def make_agent(monkeypatch):
    """Build a ProductionAgent whose primary/fallback LLMs follow the given scripts."""
    monkeypatch.setattr(agent_module, "ChatOpenAI", ScriptedLLM)
    monkeypatch.setattr(agent_module, "print_llm_info", lambda llm: None)
    monkeypatch.setattr(agent_module, "save_graph_png", lambda graph, name: None)

    def _make(primary=(), fallback=(), max_retries=3):
        agent = ProductionAgent()
        agent.primary_llm = ScriptedLLM(primary)
        agent.fallback_llm = ScriptedLLM(fallback)
        agent.max_retries = max_retries  # read by the graph at call time
        return agent

    return _make


# === Construction ===
class TestInit:
    def test_llms_are_configured_from_settings(self, make_agent, monkeypatch):
        created = []

        class RecordingLLM(ScriptedLLM):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                created.append(self)

        monkeypatch.setattr(agent_module, "ChatOpenAI", RecordingLLM)
        monkeypatch.setattr(agent_module, "print_llm_info", lambda llm: None)
        monkeypatch.setattr(agent_module, "save_graph_png", lambda graph, name: None)

        agent = ProductionAgent()
        settings = agent_module.get_settings()

        primary, fallback = created
        assert primary.init_kwargs["model"] == settings.primary_model
        assert fallback.init_kwargs["model"] == settings.fallback_model
        for llm in created:
            # retries are done by the graph topology, not the OpenAI client
            assert llm.init_kwargs["max_retries"] == 0
            assert llm.init_kwargs["temperature"] == 0
        assert agent.max_retries == settings.max_retries

    def test_graph_has_expected_nodes(self, make_agent):
        nodes = set(make_agent().graph.get_graph().nodes)

        assert {"process", "fallback", "error"} <= nodes

    def test_graph_png_is_saved(self, monkeypatch):
        saved = []
        monkeypatch.setattr(agent_module, "ChatOpenAI", ScriptedLLM)
        monkeypatch.setattr(agent_module, "print_llm_info", lambda llm: None)
        monkeypatch.setattr(
            agent_module, "save_graph_png", lambda graph, name: saved.append(name)
        )

        ProductionAgent()

        assert saved == ["graph_production_api.png"]


# === Primary succeeds ===
class TestPrimarySuccess:
    def test_returns_primary_response(self, make_agent):
        agent = make_agent(primary=["Hi there"])

        result = agent.invoke("Hello")

        assert result == {"response": "Hi there", "model_used": "primary", "error": None}

    def test_fallback_not_called(self, make_agent):
        agent = make_agent(primary=["Hi there"])
        agent.invoke("Hello")

        assert len(agent.primary_llm.calls) == 1
        assert agent.fallback_llm.calls == []

    def test_user_message_is_sent_to_llm(self, make_agent):
        agent = make_agent(primary=["ok"])
        agent.invoke("What is Python?")

        sent = agent.primary_llm.calls[0]
        assert len(sent) == 1
        assert isinstance(sent[0], HumanMessage)
        assert sent[0].content == "What is Python?"

    def test_each_invoke_starts_with_fresh_state(self, make_agent):
        agent = make_agent(primary=["first", "second"])
        agent.invoke("one")
        agent.invoke("two")

        # no conversation carry-over between invocations
        assert [m.content for m in agent.primary_llm.calls[1]] == ["two"]


# === Primary fails, fallback takes over ===
class TestFallback:
    def test_fallback_used_when_primary_fails(self, make_agent):
        agent = make_agent(primary=[RuntimeError("primary down")], fallback=["from fallback"])

        result = agent.invoke("Hello")

        assert result == {
            "response": "from fallback",
            "model_used": "fallback",
            "error": None,
        }
        assert len(agent.primary_llm.calls) == 1
        assert len(agent.fallback_llm.calls) == 1

    def test_fallback_receives_same_messages(self, make_agent):
        agent = make_agent(primary=[RuntimeError("down")], fallback=["ok"])
        agent.invoke("Hello")

        assert [m.content for m in agent.fallback_llm.calls[0]] == ["Hello"]

    def test_primary_is_retried_when_fallback_also_fails(self, make_agent):
        # primary x1 fails -> fallback fails -> primary retried and succeeds
        agent = make_agent(
            primary=[RuntimeError("p1"), "primary recovered"],
            fallback=[RuntimeError("f1")],
        )

        result = agent.invoke("Hello")

        assert result["response"] == "primary recovered"
        assert result["model_used"] == "primary"
        assert result["error"] is None
        assert len(agent.primary_llm.calls) == 2
        assert len(agent.fallback_llm.calls) == 1


# === Everything fails ===
class TestErrorHandler:
    def test_graceful_message_when_all_attempts_fail(self, make_agent):
        agent = make_agent(
            primary=[RuntimeError("p")] * 3,
            fallback=[RuntimeError("f")] * 3,
            max_retries=3,
        )

        result = agent.invoke("Hello")

        assert result["response"] == ERROR_MESSAGE
        assert result["model_used"] == "error_handler"

    def test_error_detail_is_reported(self, make_agent):
        agent = make_agent(primary=[RuntimeError("primary boom")] * 3, fallback=[RuntimeError("f")] * 3)

        # error holds the last primary failure; the handler does not clear it
        assert agent.invoke("Hello")["error"] == "primary boom"

    def test_retry_budget_is_respected(self, make_agent):
        agent = make_agent(
            primary=[RuntimeError("p")] * 3,
            fallback=[RuntimeError("f")] * 3,
            max_retries=3,
        )
        agent.invoke("Hello")

        # primary attempts 1..3; after the 3rd, retry_count (3) is no longer < max_retries
        assert len(agent.primary_llm.calls) == 3
        assert len(agent.fallback_llm.calls) == 2

    @pytest.mark.parametrize("max_retries", [1, 2, 4])
    def test_attempts_scale_with_max_retries(self, make_agent, max_retries):
        agent = make_agent(
            primary=[RuntimeError("p")] * max_retries,
            fallback=[RuntimeError("f")] * max_retries,
            max_retries=max_retries,
        )
        result = agent.invoke("Hello")

        assert result["model_used"] == "error_handler"
        assert len(agent.primary_llm.calls) == max_retries
        assert len(agent.fallback_llm.calls) == max_retries - 1

    def test_zero_retries_goes_straight_to_error_handler(self, make_agent):
        agent = make_agent(primary=[RuntimeError("p")], max_retries=0)

        result = agent.invoke("Hello")

        assert result["model_used"] == "error_handler"
        assert agent.fallback_llm.calls == []

    def test_invoke_does_not_raise_on_llm_failure(self, make_agent):
        agent = make_agent(primary=[ValueError("bad")] * 3, fallback=[TimeoutError("slow")] * 3)

        agent.invoke("Hello")  # must not raise
