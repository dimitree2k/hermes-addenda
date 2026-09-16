from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from gateway.config import PlatformConfig
from yeoman_a2a import profile, protocol
from yeoman_a2a.transport import YeomanA2AAdapter


FULL_REPORT = """# AAPL — Analyse

## Entscheidung

**HOLD** — valuation is balanced.

## Begründung

- Stable earnings support the position.
- Market risk remains manageable.

## Fundamentaldaten

Revenue and margins remain stable.

## Risiken

Macro volatility could weaken demand.
"""


def _pending(**input_overrides):
    input_data = {
        "question": "Analyse AAPL.",
        "output_format": "markdown",
        "idempotency_key": "trading-test-001",
        **input_overrides,
    }
    return {
        "task_id": "task-trading-test",
        "context_id": "ctx-trading-test",
        "peer": "yeoman",
        "started": 0.0,
        "invocation": {"skill": "trading.analyze", "input": input_data},
    }


def _store(report: str, calls: list[tuple[str, str]], available: bool = True):
    def read_report(ticker, trade_date):
        calls.append((str(ticker), str(trade_date)))
        return report if available else ""

    return SimpleNamespace(load_watchlist=lambda: ["AAPL"], read_report=read_report)


def test_missing_length_defaults_to_short_and_forwards_markdown(monkeypatch):
    calls_to_store: list[tuple[str, str]] = []
    ran = {"value": False}

    def read_report(ticker, trade_date):
        calls_to_store.append((ticker, trade_date))
        return FULL_REPORT if ran["value"] else ""

    store = SimpleNamespace(load_watchlist=lambda: ["AAPL"], read_report=read_report)
    from tools.registry import registry

    adapter = YeomanA2AAdapter(PlatformConfig(enabled=True))
    adapter._native_trading_store = lambda: store  # type: ignore[method-assign]
    resolved = []
    adapter._resolve_task = lambda task_id, state, reply: resolved.append((task_id, state, reply))  # type: ignore[method-assign]

    def dispatch(name, args):
        ran["value"] = True
        assert name == "tradingagents_analyze"
        assert args["output_format"] == "markdown"
        assert args["length"] == "short"
        return json.dumps({"date": "2026-09-17", "results": [{"ticker": "AAPL", "date": "2026-09-17", "decision_summary": "short card"}]})

    monkeypatch.setattr(registry, "dispatch", dispatch)
    adapter._run_tradingagents(_pending())

    assert resolved[0][1] == protocol.STATE_COMPLETED
    assert resolved[0][2] == FULL_REPORT
    assert calls_to_store[-1] == ("AAPL", "2026-09-17")


@pytest.mark.parametrize("length", ["short", "long", "full"])
def test_all_lengths_return_the_same_lossless_stored_report_without_rerun(monkeypatch, length):
    store_calls: list[tuple[str, str]] = []
    store = _store(FULL_REPORT, store_calls)
    adapter = YeomanA2AAdapter(PlatformConfig(enabled=True))
    adapter._native_trading_store = lambda: store  # type: ignore[method-assign]
    resolved = []
    adapter._resolve_task = lambda task_id, state, reply: resolved.append((task_id, state, reply))  # type: ignore[method-assign]

    from tools.registry import registry

    def no_run(*_args, **_kwargs):
        raise AssertionError("a stored report must not trigger TradingAgents")

    monkeypatch.setattr(registry, "dispatch", no_run)
    adapter._run_tradingagents(_pending(length=length, date="2026-09-17"))

    assert resolved == [("task-trading-test", protocol.STATE_COMPLETED, FULL_REPORT)]
    assert store_calls == [("AAPL", "2026-09-17")]


def test_invalid_length_is_rejected_before_execution(monkeypatch):
    adapter = YeomanA2AAdapter(PlatformConfig(enabled=True))
    adapter._native_trading_store = lambda: _store(FULL_REPORT, [])  # type: ignore[method-assign]
    resolved = []
    adapter._resolve_task = lambda task_id, state, reply: resolved.append((task_id, state, reply))  # type: ignore[method-assign]

    adapter._run_tradingagents(_pending(length="medium"))

    assert resolved[0][1] == protocol.STATE_FAILED
    assert "INVALID_LENGTH" in resolved[0][2]


def test_long_or_full_without_saved_report_is_structured_error_and_never_runs(monkeypatch):
    adapter = YeomanA2AAdapter(PlatformConfig(enabled=True))
    adapter._native_trading_store = lambda: _store("", [], available=False)  # type: ignore[method-assign]
    resolved = []
    adapter._resolve_task = lambda task_id, state, reply: resolved.append((task_id, state, reply))  # type: ignore[method-assign]
    from tools.registry import registry
    monkeypatch.setattr(registry, "dispatch", lambda *_args: (_ for _ in ()).throw(AssertionError("rerun")))

    pending = _pending(length="full", date="2026-09-17")
    adapter._run_tradingagents(pending)

    assert resolved[0][1] == protocol.STATE_FAILED
    assert pending["failure"] == {
        "code": "REPORT_NOT_FOUND",
        "message": "No stored TradingAgents report for AAPL on 2026-09-17; run a short analysis first.",
    }


def test_report_cleanup_removes_escaped_lines_reasoning_fences_and_internal_paths():
    dirty = (
        "**Reasoning:** inspect the report\n"
        "```markdown\n"
        "# AAPL — Analyse\n\n"
        "## Entscheidung\n\n**BUY** — momentum.\n\n"
        "Saved at /home/deploy/.hermes/tradingagents/reports/aapl.md\\n"
        "```"
    )

    report = YeomanA2AAdapter._clean_trading_report(dirty)

    assert report.startswith("# AAPL — Analyse")
    assert "**Reasoning:**" not in report
    assert "```" not in report
    assert "/home/deploy/.hermes" not in report
    assert "\\n" not in report
    assert "\n## Entscheidung" in report


def test_full_report_is_not_the_native_summary_and_result_keeps_correlation():
    result = profile.result_for_reply(
        "trading.analyze",
        FULL_REPORT,
        task_id="task-123",
        context_id="ctx-123",
        reference_task_ids=["ref-1", "ref-2"],
    )

    profile.validate_result(result)
    assert result["output"]["report"] == FULL_REPORT
    assert result["output"]["sources"] == []
    assert result["correlation"] == {
        "task_id": "task-123",
        "context_id": "ctx-123",
        "reference_task_ids": ["ref-1", "ref-2"],
    }


def test_profile_rejects_json_envelope_as_trading_report():
    with pytest.raises(profile.ContractViolation, match="serialized JSON"):
        profile.result_for_reply("trading.analyze", json.dumps({"report": FULL_REPORT}))


def test_schema_rejects_alias_and_invalid_length():
    with pytest.raises(profile.ContractViolation):
        profile.validate_skill_request("trading.analyze", {
            "question": "Analyse AAPL.",
            "output_format": "markdown",
            "length": "medium",
            "idempotency_key": "invalid-length",
        })
    with pytest.raises(profile.ContractViolation):
        profile.validate_skill_request("trading.analyze", {
            "question": "Analyse AAPL.",
            "output_format": "markdown",
            "full_length": True,
            "idempotency_key": "alias",
        })
