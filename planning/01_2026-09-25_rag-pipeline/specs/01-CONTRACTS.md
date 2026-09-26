# Hợp đồng dữ liệu và hàm
Nguồn: [MODULE_CONTRACTS](../../../docs/MODULE_CONTRACTS.md) và [validators](../../../src/contracts.py).

## Schema bắt buộc
- Document: {id: str, content: str, metadata: {source: str, title: str, doc_type: legal|news, url: str|null}}.
- Chunk: Document + metadata.chunk_index: int ≥0.
- EmbeddedChunk: Chunk + embedding: list[float].
- SearchResult: Chunk + score: float + retrieval_method: dense|bm25|hybrid|pageindex.
- GenerationResult: {answer: str, sources: list[SearchResult], retrieval_source: hybrid|pageindex|none}.
- News JSON: {url, title, date_crawled, content_markdown}, mọi giá trị có nội dung.
- Golden row: {question, expected_answer, expected_context}, mọi giá trị có nội dung; có thể thêm source IDs để truy vết.

## Chữ ký giữ nguyên
```python
load_documents() -> list[dict]
chunk_documents(documents: list[dict]) -> list[dict]
embed_texts(texts: list[str]) -> list[list[float]]
embed_chunks(chunks: list[dict]) -> list[dict]
get_collection()
index_to_vectorstore(chunks: list[dict]) -> None
semantic_search(query: str, top_k: int = 10) -> list[dict]
lexical_search(query: str, top_k: int = 10) -> list[dict]
rerank_rrf(ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60) -> list[dict]
pageindex_search(query: str, top_k: int = 5) -> list[dict]
retrieve(query: str, top_k: int = 5, score_threshold: float = 0.3, use_reranking: bool = True) -> list[dict]
reorder_for_llm(chunks: list[dict]) -> list[dict]
format_context(chunks: list[dict]) -> str
call_llm(system_prompt: str, user_message: str) -> str
generate_with_citation(query: str, top_k: int = 5) -> dict
```
Defaults 0.3/5 là hiện trạng, chưa phải kết quả calibration.

## Quy tắc và lỗi
BẮT BUỘC output search unique ID, score hữu hạn giảm dần, count ≤ max(top_k,0).
Query trắng hoặc top_k ≤0 trả []; generation không có evidence trả refusal.
CẤM lấy thứ tự context đã reorder làm thay đổi thứ tự sources theo score; citation dùng ID chunk ổn định.
CẤM trả retrieval_source=dense hoặc bm25: nhánh non-PageIndex có nguồn được biểu diễn hybrid ở envelope, giữ retrieval_method gốc bên trong.
| Lỗi | Caller |
| :-- | :-- |
| Schema thiếu field | Validator ValueError; ingest báo và dừng item |
| Dimension/model không khớp collection | Dừng indexing/query, thông báo rebuild có kiểm soát |
| NaN/Infinity hoặc ID trùng từ provider | Chuẩn hóa/loại item trước trả output, log không chứa key |

## Bằng chứng
python -m pytest tests/test_contracts.py -q phải exit 0 khi thi công xong.
Bổ sung ca rỗng, top_k ≤0, tie, score không hữu hạn, idempotency và citation mapping; mock network.
Hiện trạng đo trong [baseline](../evidence/P00/baseline-tests.txt), chưa đạt contract suite.
