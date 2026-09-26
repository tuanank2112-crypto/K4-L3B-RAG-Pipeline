"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import math
import re
import numpy as np
from rank_bm25 import BM25Okapi


CORPUS: list[dict] = []


def get_corpus() -> list[dict]:
    """Lấy corpus hiện hành hoặc tự nạp chunks từ data/standardized/."""
    global CORPUS
    if not CORPUS:
        try:
            from .task4_chunking_indexing import load_documents, chunk_documents
            docs = load_documents()
            if docs:
                CORPUS = chunk_documents(docs)
        except Exception:
            pass
    return CORPUS


class RobustBM25Okapi(BM25Okapi):
    """BM25Okapi với Lucene-style non-zero IDF smoothing để xử lý corpus nhỏ/ngắn."""

    def _calc_idf(self, nd):
        for word, freq in nd.items():
            self.idf[word] = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))


def tokenize_text(text: str) -> list[str]:
    """Tách từ chuẩn, bỏ dấu câu để tăng khả năng so khớp tiếng Việt."""
    return re.findall(r"\w+", text.lower(), re.UNICODE)


def expand_query(query: str) -> str:
    """Mở rộng từ viết tắt thường gặp trong bối cảnh sinh viên đại học."""
    expanded = query.lower()
    replacements = {
        r"\bktx\b": "ktx ký túc xá nội trú",
        r"\bđkhp\b": "đkhp đăng ký học phần",
        r"\bdkhp\b": "dkhp đăng ký học phần môn học",
        r"\bclb\b": "clb câu lạc bộ",
        r"\bgpa\b": "gpa điểm trung bình",
        r"\bcgpa\b": "cgpa điểm tích lũy toàn khóa",
        r"\bhọc bổng\b": "học bổng tài năng hỗ trợ tài chính",
        r"\bhọc phí\b": "học phí nộp tiền thanh toán",
    }
    for pattern, repl in replacements.items():
        expanded = re.sub(pattern, repl, expanded)
    return expanded


def build_bm25_index(corpus: list[dict]) -> BM25Okapi:
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    tokenized = [tokenize_text(item["content"]) for item in corpus]
    return RobustBM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    active_corpus = get_corpus()
    if not query or not query.strip() or top_k <= 0 or not active_corpus:
        return []

    bm25 = build_bm25_index(active_corpus)
    enriched_query = expand_query(query)
    query_tokens = tokenize_text(enriched_query)
    if not query_tokens:
        return []

    scores = bm25.get_scores(query_tokens)
    indices = np.argsort(scores)[::-1]

    results_by_id: dict[str, dict] = {}
    for index in indices:
        score = float(scores[index])
        if score <= 0.0:
            continue
        item = active_corpus[index]
        item_id = str(item["id"])
        meta = dict(item["metadata"])
        if not meta.get("url"):
            meta["url"] = None
        if "chunk_index" in meta:
            meta["chunk_index"] = int(meta["chunk_index"])

        if item_id in results_by_id:
            if score > float(results_by_id[item_id]["score"]):
                results_by_id[item_id]["score"] = score
        else:
            results_by_id[item_id] = {
                "id": item_id,
                "content": str(item["content"]),
                "score": score,
                "metadata": meta,
                "retrieval_method": "bm25",
            }

    sorted_results = sorted(
        results_by_id.values(),
        key=lambda item: (-float(item["score"]), item["id"]),
    )
    return sorted_results[:top_k]


if __name__ == "__main__":
    for result in lexical_search("ở ktx cần chú ý gì?", top_k=3):
        print(result["id"], result["score"])
