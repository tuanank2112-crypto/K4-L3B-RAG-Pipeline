import sys
from types import SimpleNamespace

import pytest

from src import task4_chunking_indexing as indexing
from src import task10_generation as generation


def chunk():
    return {"id": "legal/a.md::chunk-0", "content": "Tuition policy", "score": 0.9,
            "retrieval_method": "dense", "metadata": {"source": "a.pdf", "title": "A",
            "doc_type": "legal", "url": None, "chunk_index": 0}}


@pytest.mark.parametrize("answer", ["", "Unsupported assertion", "Assertion [invented]"])
def test_invalid_citations_refuse(monkeypatch, answer):
    monkeypatch.setattr(generation, "retrieve", lambda *a, **k: [chunk()])
    monkeypatch.setattr(generation, "call_llm", lambda *a: answer)
    result = generation.generate_with_citation("tuition")
    assert result["retrieval_source"] == "none"
    assert result["sources"] == []
    assert result["answer"]


def test_provider_error_does_not_leak(monkeypatch):
    monkeypatch.setattr(generation, "retrieve", lambda *a, **k: [chunk()])
    def broken(*args):
        raise RuntimeError("secret-api-key")
    monkeypatch.setattr(generation, "call_llm", broken)
    result = generation.generate_with_citation("tuition")
    assert "secret-api-key" not in result["answer"]
    assert result["sources"] == []


def test_gemini_plural_embeddings(monkeypatch):
    from google import genai
    monkeypatch.setenv("EMBEDDING_PROVIDER", "gemini")
    fake = SimpleNamespace(models=SimpleNamespace(embed_content=lambda **k:
        SimpleNamespace(embeddings=[SimpleNamespace(values=[0.1, 0.2]), SimpleNamespace(values=[0.3, 0.4])])))
    monkeypatch.setattr(genai, "Client", lambda **k: fake)
    assert indexing.embed_texts(["a", "b"]) == [[0.1, 0.2], [0.3, 0.4]]


@pytest.mark.parametrize("vectors", [[[1.0]], [[1.0], [1.0, 2.0]], [[float("nan")], [1.0]]])
def test_embed_chunks_rejects_invalid_vectors(monkeypatch, vectors):
    monkeypatch.setattr(indexing, "embed_texts", lambda texts: vectors)
    with pytest.raises(ValueError):
        indexing.embed_chunks([chunk(), {**chunk(), "id": "other"}])


def test_loader_metadata_and_legacy_exclusion(monkeypatch, tmp_path):
    monkeypatch.setattr(indexing, "STANDARDIZED_DIR", tmp_path)
    (tmp_path / "legal").mkdir()
    (tmp_path / "legal/a.md").write_text("# Original title\n**Verified:** true\n**Source:** old.pdf\n**File:** a.pdf\n\nText", encoding="utf-8")
    (tmp_path / "legal/old.md").write_text("# Legacy\nFake", encoding="utf-8")
    docs = indexing.load_documents()
    assert len(docs) == 1
    assert docs[0]["metadata"] == {"title": "Original title", "source": "a.pdf", "url": None, "doc_type": "legal"}
