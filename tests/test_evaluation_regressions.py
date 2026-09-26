import json

import pytest

from src import evaluate as ev


def case():
    return {"question": "alpha beta", "expected_answer": "alpha", "expected_context": "alpha", "source_ids": ["doc"]}


def test_missing_config_has_no_fabricated_score():
    report = ev.generate_report(None, None)
    assert "0.6325" not in report
    assert "0.9050" not in report
    assert "chưa đo" in report.lower()
    assert "+0.03" not in report


@pytest.mark.parametrize("config", ["dense_only", "hybrid_rrf"])
def test_dense_error_propagates(config, monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("secret-api-key")
    monkeypatch.setattr(ev, "semantic_search", broken)
    with pytest.raises(RuntimeError):
        ev.run_pipeline_config(config, "query")


def test_failed_case_has_null_metrics_and_incomplete_run(monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("secret-api-key")
    monkeypatch.setattr(ev, "run_pipeline_config", broken)
    result = ev.evaluate_dataset("dense_only", [case()])
    assert result["status"] == "incomplete"
    assert result["overall"] is None
    assert result["cases"][0]["metrics"] is None
    assert "secret-api-key" not in json.dumps(result)


def test_no_relevance_floor_or_refusal_reward():
    assert ev.compute_answer_relevance("alpha beta", "alpha many unrelated words are here") == 0.5
    assert ev.compute_faithfulness("Tôi không thể xác minh", []) == 0


def test_golden_requires_grounded_sources():
    documents = [{"id": "doc", "content": "alpha", "metadata": {"url": "https://example.org/doc"}}]
    ev.validate_golden([case()] * 15, documents)
    with pytest.raises(ValueError):
        ev.validate_golden([{**case(), "source_ids": ["invented"]}] * 15, documents)
    with pytest.raises(ValueError):
        ev.validate_golden([{**case(), "expected_context": "invented quote"}] * 15, documents)


def test_shared_generation_and_raw_sources(monkeypatch):
    chunks = [{"id": "doc::chunk-0", "content": "alpha", "score": 1.0, "metadata": {}}]
    monkeypatch.setattr(ev, "semantic_search", lambda *a, **kw: chunks)
    monkeypatch.setattr(ev, "generate_from_chunks", lambda query, source: {"answer": "alpha", "sources": source, "retrieval_source": "hybrid"})
    result = ev.evaluate_dataset("dense_only", [case()])
    assert result["status"] == "complete"
    assert result["cases"][0]["sources"] == chunks


def test_partial_results_do_not_publish_aggregate(monkeypatch):
    calls = iter([({"answer": "alpha", "sources": []}, 0.1), RuntimeError("private")])
    def run(*a, **kw):
        result = next(calls)
        if isinstance(result, Exception):
            raise result
        return result
    monkeypatch.setattr(ev, "run_pipeline_config", run)
    result = ev.evaluate_dataset("dense_only", [case(), case()])
    assert result["successful_cases"] == 1
    assert result["overall"] is None


def test_main_incomplete_exits_nonzero_and_writes_artifact(monkeypatch, tmp_path):
    golden = tmp_path / "golden.json"
    golden.write_text(json.dumps([case()] * 15))
    monkeypatch.setattr(ev, "GOLDEN_PATH", golden)
    monkeypatch.setattr(ev, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(ev, "RESULT_MD_PATH", tmp_path / "RESULT.md")
    monkeypatch.setattr(ev, "REPORTS_RESULT_MD", tmp_path / "report.md")
    monkeypatch.setattr(ev, "load_documents", lambda: [{"id": "doc", "content": "alpha", "metadata": {"url": "https://example.org/doc"}}])
    monkeypatch.setattr(ev, "evaluate_dataset", lambda *a, **kw: {"status": "incomplete", "overall": None, "cases": []})
    assert ev.main(["--config", "A"]) == 1
    run = json.loads(next((tmp_path / "runs").glob("*/results.json")).read_text())
    assert run["status"] == "incomplete"
    assert run["fingerprints"]["golden_sha256"]


def test_report_uses_actual_direction_and_labels():
    def result(score):
        return {"status": "complete", "overall": {**dict.fromkeys(ev.METRICS, score), "average": score, "avg_latency_sec": 1},
                "cases": [{"id": 1, "question": "example", "metrics": dict.fromkeys(ev.METRICS, score)}]}
    assert "B thấp hơn A" in ev.generate_report(result(0.9), result(0.1))
    only_a = ev.generate_report(result(0.9), None)
    assert "| A | 1 | example" in only_a
    assert "| B | 1 | example" not in only_a
    assert "không công bố delta" in only_a


def test_generation_failure_unscored(monkeypatch):
    monkeypatch.setattr(ev, "semantic_search", lambda *a, **kw: [{"id": "x", "content": "alpha"}])
    def broken(*a, **kw):
        raise ValueError("private provider response")
    monkeypatch.setattr(ev, "generate_from_chunks", broken)
    result = ev.evaluate_dataset("dense_only", [case()])
    assert result["cases"][0]["status"] == "error"
    assert result["cases"][0]["metrics"] is None


def test_validation_prevents_provider_calls(monkeypatch, tmp_path):
    golden = tmp_path / "golden.json"
    golden.write_text("[]")
    monkeypatch.setattr(ev, "GOLDEN_PATH", golden)
    monkeypatch.setattr(ev, "load_documents", lambda: [])
    def forbidden(*a, **kw):
        pytest.fail("Provider evaluation must not start")
    monkeypatch.setattr(ev, "evaluate_dataset", forbidden)
    assert ev.main([]) == 2


def test_changed_fingerprint_prevents_comparison(monkeypatch, tmp_path):
    golden = tmp_path / "golden.json"
    golden.write_text(json.dumps([case()] * 15))
    monkeypatch.setattr(ev, "GOLDEN_PATH", golden)
    monkeypatch.setattr(ev, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(ev, "RESULT_MD_PATH", tmp_path / "RESULT.md")
    monkeypatch.setattr(ev, "REPORTS_RESULT_MD", tmp_path / "report.md")
    monkeypatch.setattr(ev, "load_documents", lambda: [{"id": "doc", "content": "alpha", "metadata": {"url": "https://example.org/doc"}}])
    signatures = iter([{"corpus_sha256": "before"}, {"corpus_sha256": "after"}])
    monkeypatch.setattr(ev, "fingerprints", lambda *a: next(signatures))
    monkeypatch.setattr(ev, "evaluate_dataset", lambda *a: {"status": "complete", "overall": {"average": 1}, "cases": []})
    assert ev.main([]) == 1
    artifact = json.loads(next((tmp_path / "runs").glob("*/results.json")).read_text())
    assert artifact["inputs_unchanged"] is False
    assert artifact["results_a"]["overall"] is None
    assert artifact["results_b"]["overall"] is None
