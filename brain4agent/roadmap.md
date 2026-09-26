## Trạng thái 2026-09-26T10:38:00+07:00 — H01–H04 Hoàn Tất Thẩm Định, Sẵn Sàng Nghiệm Thu
Đã hoàn thành toàn bộ các hạng mục theo SPEC-P05 và handoffs:
- H01: Loader đọc 8 tài liệu thật verified, chuẩn hóa tiếng Việt cho generation.
- H02: Runner evaluate loại bỏ số mặc định, bắt lỗi an toàn (metrics=null, status=error).
- H03: Tích hợp 8 tài liệu thật, 560 chunks, 16 ca golden có ground-truth thật; nạp live keys Jina + Gemini.
- H04: Thẩm định độc lập 🔴 hoàn tất, đo đạc toàn bộ exit gates (42/42 tests pass, mypy/ruff/compileall exit 0, 3 adversarial tests pass), nộp report R04 phán quyết DUYỆT.

# Roadmap
## Active
[Kế hoạch 01 — RAG Pipeline](../planning/01_2026-09-25_rag-pipeline/plan.md): 🟢 Đã thẩm định hoàn tất (H01–H04 nộp đủ report; chờ người duyệt chốt nghiệm thu).

## Done
- [x] 2026-09-25: tích hợp engine 1.13.1, khung 1.7.1.
- [x] 2026-09-25: lập SPEC package, ghi baseline và đồng bộ não.
- [x] 2026-09-26: khắc phục triệt để 7 findings sau review (corpus thật, metadata URL, live keys Jina + Gemini, benchmark A/B thật không điểm giả, Safe Refusal & citation validation).
- [x] 2026-09-26: hoàn thành H01, H02, H03 và H04 thẩm định độc lập.

## Cần sửa sau review (Đã khắc phục 100%)
- [x] Corpus thật và metadata URL nguồn (3 legal PDF sha256 + 5 news JSON verified).
- [x] Live embedding Jina (jina-embeddings-v3), generation Gemini (gemini-3.5-flash-lite), kiểm soát citation.
- [x] Benchmark không điền số giả định, không che lỗi dense; đo A/B thật 16/16 cases complete (run_20260926_032209_492532).
- [x] Cập nhật báo cáo và nghiệm thu lại có evidence đầy đủ trong evidence/audit/.

## Idea Vault
HyDE/query expansion; reranker nâng cao; conversation memory; citation highlighting/deploy.
Chỉ xem xét sau core, mỗi bonus phải có demo hoặc số đo A/B.
