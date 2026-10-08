"""Unit tests for app.common (no server, network, or API key needed)."""

from types import SimpleNamespace

from app.common import print_llm_info, print_section, save_graph_png

BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"


class FakeGraph:
    def __init__(self, png_bytes: bytes):
        self._png = png_bytes

    def draw_mermaid_png(self) -> bytes:
        return self._png


class FakeApp:
    def __init__(self, png_bytes: bytes):
        self._graph = FakeGraph(png_bytes)

    def get_graph(self) -> FakeGraph:
        return self._graph


class TestPrintSection:
    def test_prints_name_between_borders(self, capsys):
        print_section("My Section")
        out = capsys.readouterr().out
        border = "#" * 60
        assert f"{border}\n# My Section\n{border}" in out

    def test_wrapped_in_blue_and_reset(self, capsys):
        print_section("X")
        out = capsys.readouterr().out
        assert out.startswith(f"\n{BLUE}")
        assert out.rstrip("\n").endswith(RESET)

    def test_returns_none(self):
        assert print_section("X") is None


class TestSaveGraphPng:
    def test_writes_png_bytes(self, tmp_path):
        target = tmp_path / "graph.png"
        payload = b"\x89PNG\r\n\x1a\nfake-bytes"
        save_graph_png(FakeApp(payload), str(target))
        assert target.read_bytes() == payload

    def test_overwrites_existing_file(self, tmp_path):
        target = tmp_path / "graph.png"
        target.write_bytes(b"old-content-that-is-longer")
        save_graph_png(FakeApp(b"new"), str(target))
        assert target.read_bytes() == b"new"

    def test_prints_confirmation(self, tmp_path, capsys):
        target = tmp_path / "graph.png"
        save_graph_png(FakeApp(b"x"), str(target))
        out = capsys.readouterr().out
        assert out == f"{YELLOW}Graph saved to {target}{RESET}\n"


class TestPrintLlmInfo:
    def test_prints_model_name(self, capsys):
        print_llm_info(SimpleNamespace(model_name="gpt-4o-mini"))
        out = capsys.readouterr().out
        assert out == f"{YELLOW}Using LLM: gpt-4o-mini{RESET}\n"
