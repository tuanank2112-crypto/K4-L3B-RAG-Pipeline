"""Reproducible dense/hybrid benchmark; token heuristics are not semantic RAGAS."""

import argparse
import datetime
import hashlib
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import time
from urllib.parse import urlsplit

from dotenv import load_dotenv

from . import task10_generation as generation
from .task4_chunking_indexing import load_documents
from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf

load_dotenv()
ROOT_DIR = Path(__file__).parent.parent
GOLDEN_PATH = ROOT_DIR / "group_project/evaluation/golden_dataset.json"
RUNS_DIR = ROOT_DIR / "group_project/evaluation/runs"
RESULT_MD_PATH = ROOT_DIR / "group_project/evaluation/RESULT.md"
REPORTS_RESULT_MD = ROOT_DIR / "reports/RESULT.md"
METRICS = ("faithfulness", "answer_relevance", "context_recall", "context_precision")


def generate_from_chunks(query: str, chunks: list[dict]) -> dict:
    """Delegate to the exact generator used by the application, preserving errors."""
    return generation.generate_from_chunks(query, chunks)


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower(), re.UNICODE))


def overlap_recall(expected: str, actual: str) -> float:
    target = tokenize(expected)
    return len(target & tokenize(actual)) / len(target) if target else 0.0


def compute_context_recall(expected_context: str, retrieved_chunks: list[dict]) -> float:
    return overlap_recall(expected_context, " ".join(c["content"] for c in retrieved_chunks))


def compute_context_precision(expected_answer: str, retrieved_chunks: list[dict]) -> float:
    """Average precision of chunks with >=25% expected-answer token coverage."""
    hits = [overlap_recall(expected_answer, c["content"]) >= 0.25 for c in retrieved_chunks]
    count, total = 0, 0.0
    for rank, hit in enumerate(hits, 1):
        if hit:
            count += 1
            total += count / rank
    return total / count if count else 0.0


def compute_faithfulness(generated_answer: str, retrieved_chunks: list[dict]) -> float:
    answer = re.sub(r"\[[^\]]+\]", "", generated_answer)
    return overlap_recall(answer, " ".join(c["content"] for c in retrieved_chunks))


def compute_answer_relevance(question: str, generated_answer: str) -> float:
    return overlap_recall(question, re.sub(r"\[[^\]]+\]", "", generated_answer))


def run_pipeline_config(config_name: str, query: str, top_k: int = 5) -> tuple[dict, float]:
    start = time.perf_counter()
    if config_name == "dense_only":
        chunks = semantic_search(query, top_k=top_k)
    elif config_name == "hybrid_rrf":
        dense = semantic_search(query, top_k=top_k * 2)
        sparse = lexical_search(query, top_k=top_k * 2)
        chunks = rerank_rrf([dense, sparse], top_k=top_k)
    else:
        raise ValueError("Unknown benchmark configuration")
    return generate_from_chunks(query, chunks), time.perf_counter() - start


def evaluate_dataset(config_name: str, golden_cases: list[dict], top_k: int = 5) -> dict:
    results = []
    for index, case in enumerate(golden_cases, 1):
        row = {"id": index, **case, "status": "error", "metrics": None,
               "generated_answer": None, "sources": [], "retrieved_sources": [], "latency_sec": None}
        started = time.perf_counter()
        try:
            result, latency = run_pipeline_config(config_name, case["question"], top_k)
            sources, answer = result["sources"], result["answer"]
            row.update(status="ok", generated_answer=answer, sources=sources,
                       retrieved_sources=[c["id"] for c in sources], latency_sec=latency,
                       metrics={"faithfulness": compute_faithfulness(answer, sources),
                                "answer_relevance": compute_answer_relevance(case["question"], answer),
                                "context_recall": compute_context_recall(case["expected_context"], sources),
                                "context_precision": compute_context_precision(case["expected_answer"], sources)})
        except Exception:
            # Never serialize exception strings: provider messages can include credentials.
            row.update(error={"code": "pipeline_error", "message": "Retrieval or generation failed; check provider/configuration."},
                       latency_sec=time.perf_counter() - started)
        results.append(row)
        print(f"{config_name} case {index}/{len(golden_cases)}: {row['status']}", flush=True)
    successful = sum(row["status"] == "ok" for row in results)
    complete = bool(results) and successful == len(results)
    overall = None
    if complete:
        overall = {metric: sum(row["metrics"][metric] for row in results) / len(results) for metric in METRICS}
        overall["average"] = sum(overall.values()) / len(METRICS)
        overall["avg_latency_sec"] = sum(row["latency_sec"] for row in results) / len(results)
    return {"config": config_name, "status": "complete" if complete else "incomplete",
            "successful_cases": successful, "total_cases": len(results), "overall": overall, "cases": results}


def validate_golden(cases: list[dict], documents: list[dict]) -> None:
    """Check ground truth references and verbatim context before any provider call."""
    if not isinstance(cases, list) or len(cases) < 15:
        raise ValueError("Golden dataset requires at least 15 grounded cases")
    by_id = {doc["id"]: doc for doc in documents}
    for index, row in enumerate(cases, 1):
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k].strip()
                                            for k in ("question", "expected_answer", "expected_context")):
            raise ValueError(f"Golden case {index}: invalid required fields")
        ids = row.get("source_ids")
        if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or i not in by_id for i in ids):
            raise ValueError(f"Golden case {index}: missing/unknown source_ids")
        referenced = [by_id[i] for i in ids]
        if any(urlsplit(doc.get("metadata", {}).get("url") or "").scheme not in {"http", "https"}
               or not urlsplit(doc.get("metadata", {}).get("url") or "").netloc for doc in referenced):
            raise ValueError(f"Golden case {index}: source lacks HTTP provenance")
        quote = " ".join(row["expected_context"].split())
        if not any(quote in " ".join(doc["content"].split()) for doc in referenced):
            raise ValueError(f"Golden case {index}: expected_context must quote a referenced source")


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def fingerprints(documents: list[dict], top_k: int) -> dict:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    defaults = {"openai": "gpt-4o-mini", "gemini": "gemini-2.5-flash-lite", "anthropic": "claude-3-5-haiku-latest"}
    packages: dict[str, str | None] = {}
    for package in ("openai", "google-genai", "anthropic", "chromadb", "rank-bm25", "sentence-transformers"):
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = None
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT_DIR, capture_output=True, text=True)
    corpus = sorted(documents, key=lambda doc: doc["id"])
    return {"corpus_sha256": sha256(json.dumps(corpus, sort_keys=True, ensure_ascii=False).encode()),
            "golden_sha256": sha256(GOLDEN_PATH.read_bytes()),
            "generation_sha256": sha256(inspect.getsource(generation).encode()),
            "prompt_sha256": sha256(generation.SYSTEM_PROMPT.encode()),
            "evaluator_sha256": sha256(Path(__file__).read_bytes()),
            "git_commit": commit.stdout.strip() if commit.returncode == 0 else None,
            "embedding_provider": os.getenv("EMBEDDING_PROVIDER", "openai"),
            "embedding_model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            "generator_provider": provider, "generator_model": os.getenv("LLM_MODEL", "").strip() or defaults.get(provider),
            "temperature": generation.TEMPERATURE, "seed": None,
            "top_k": top_k, "fallback_enabled": False, "rrf_k": 60,
            "python": platform.python_version(), "sdk_versions": packages,
            "source_count": len(documents), "evaluator": "token-overlap-v2 (not semantic RAGAS)"}


def generate_report(results_a: dict | None, results_b: dict | None, metadata: dict | None = None) -> str:
    def scores(result):
        return result.get("overall") if result and result.get("status", "complete") == "complete" else None
    a, b = scores(results_a), scores(results_b)
    lines = ["# RAG evaluation results", "", "## Run information", "",
             f"Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}", "",
             "```json", json.dumps(metadata or {}, ensure_ascii=False, indent=2), "```", "",
             "## Configurations", "",
             "A: dense-only. B: dense + BM25 + RRF k=60. Same corpus, top_k and shared generator; PageIndex fallback disabled.", "",
             "## Overall scores", "", "| Metric | Config A | Config B | Delta B−A |", "| --- | ---: | ---: | ---: |"]
    for metric in (*METRICS, "average", "avg_latency_sec"):
        av, bv = a.get(metric) if a else None, b.get(metric) if b else None
        fmt = lambda value: f"{value:.4f}" if value is not None else "Chưa đo / incomplete"
        delta = f"{bv-av:+.4f}" if av is not None and bv is not None else "Không so sánh"
        lines.append(f"| {metric} | {fmt(av)} | {fmt(bv)} | {delta} |")
    lines.extend(["", "## A/B comparison", ""])
    if a and b:
        delta = b["average"] - a["average"]
        outcome = "B cao hơn A" if delta > 0 else "B thấp hơn A" if delta < 0 else "A và B bằng nhau"
        lines.append(f"{outcome} trên trung bình heuristic: Delta B−A = {delta:+.4f}. Đây là số đo mô tả, chưa chứng minh ý nghĩa thống kê hay nguyên nhân.")
    else:
        lines.append("Chưa đo đủ hai cấu hình thành công; không công bố delta hoặc kết luận A/B.")
    lines.extend(["", "## Worst performers", "", "| Config | Case | Question | Mean heuristic | Observed weakest metric |", "| --- | --- | --- | ---: | --- |"])
    for label, result in (("A", results_a), ("B", results_b)):
        rows = [c for c in (result or {}).get("cases", []) if c.get("metrics")]
        for row in sorted(rows, key=lambda c: sum(c["metrics"].values()))[:3]:
            metric = min(row["metrics"], key=row["metrics"].get)
            question = row["question"].replace("|", "/").replace("\n", " ")
            lines.append(f"| {label} | {row['id']} | {question} | {sum(row['metrics'].values()) / 4:.4f} | {metric}={row['metrics'][metric]:.4f} |")
        errors = [c["id"] for c in (result or {}).get("cases", []) if c.get("status") == "error"]
        if errors:
            lines.append(f"\nConfig {label} pipeline errors (unscored): {errors}.")
    lines.extend(["", "## Recommendations", "",
                  "Đối chiếu answer, sources và expected_context của các case thấp nhất trong results.json trước khi xác định nguyên nhân; metric thấp chỉ là dấu hiệu cần kiểm tra.",
                  "Nếu có lỗi pipeline, xử lý cấu hình/provider rồi chạy lại cả A/B. Tách tập calibration khỏi golden test trước khi điều chỉnh chunk hoặc retrieval; chưa có số đo mức cải thiện kỳ vọng.", "",
                  "## Metric definitions and limitations", "",
                  "Token = tập từ Unicode viết thường; citation labels được bỏ khỏi answer. Faithfulness = |answer tokens ∩ context tokens| / |answer tokens|. Answer relevance = |question tokens ∩ answer tokens| / |question tokens|. Context recall = |expected_context tokens ∩ context tokens| / |expected_context tokens|. Context precision = average precision theo thứ hạng, chunk liên quan khi bao phủ ≥25% expected_answer tokens. Mẫu số rỗng nhận 0; không có điểm nền hoặc thưởng refusal.",
                  "Đây là token heuristics, không phải semantic RAGAS: không xác minh mâu thuẫn, phủ định, entailment, từng khẳng định hay chất lượng citation. Aggregate chỉ có khi mọi case thành công. Latency gồm retrieval/generation; chi phí và seed chưa đo/không cố định. Golden provenance kiểm quote và URL, không tự xác nhận đáp án đúng về mặt chuyên môn.", "",
                  "## Bonus experiments", "", "Chưa đo thí nghiệm bonus; không công bố điểm cộng.", ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run auditable RAG A/B evaluation")
    parser.add_argument("--config", choices=["both", "A", "B"], default="both")
    parser.add_argument("--top_k", type=int, default=5)
    args = parser.parse_args(argv)
    try:
        if args.top_k <= 0:
            raise ValueError("top_k must be positive")
        cases = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
        documents = load_documents()
        validate_golden(cases, documents)
    except (ValueError, OSError, KeyError, TypeError):
        print("Golden/corpus validation failed; check required fields, source_ids, HTTP provenance and exact context quotes.")
        return 2
    before = fingerprints(documents, args.top_k)
    a = evaluate_dataset("dense_only", cases, args.top_k) if args.config in {"both", "A"} else None
    b = evaluate_dataset("hybrid_rrf", cases, args.top_k) if args.config in {"both", "B"} else None
    after = fingerprints(load_documents(), args.top_k)
    comparable = before == after
    complete = comparable and all(r["status"] == "complete" for r in (a, b) if r is not None)
    if not comparable:
        for result in (a, b):
            if result:
                result.update(status="incomplete", overall=None)
    run_id = datetime.datetime.now(datetime.timezone.utc).strftime("run_%Y%m%d_%H%M%S_%f")
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    run = {"run_id": run_id, "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "status": "complete" if complete else "incomplete", "top_k": args.top_k,
           "fingerprints": before, "fingerprints_after": after, "inputs_unchanged": comparable,
           "results_a": a, "results_b": b}
    (run_dir / "results.json").write_text(json.dumps(run, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    report = generate_report(a, b, {"run_id": run_id, "status": run["status"], "golden_size": len(cases), **before})
    for path in (RESULT_MD_PATH, REPORTS_RESULT_MD):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")
    print(f"Run {run_id}: {run['status']}")
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
