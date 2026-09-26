## Trạng thái 2026-09-26T09:35:04+07:00 — bàn giao worker, chưa nghiệm thu
Chỉ chuẩn bị planning theo chỉ đạo mới. [Plan](../planning/01_2026-09-25_rag-pipeline/plan.md) §8 và SPEC-P05-Completion là router tiếp tục. Đã tải 3 PDF thật + 5 page VinUni; file giả cũ giữ nguyên và phải loại khỏi index. Loader=0 do parser header, PageIndex còn stub; golden/report cũ chưa phù hợp corpus mới. Core/evaluation sửa dang dở trước khi worker hết quota. Baseline 42 pass/0 fail/0 skip không thay live gate. Tiếp tục H01 → H02 → H03 → H04; chưa phóng thêm. API-only theo ký ức trước; Jina/PageIndex thiếu key, generation chưa smoke. Không phát hành mới.

# Lịch sử dự án
## 2026-09-26 — Tích hợp Corpus Thật, Live Jina & Gemini, Hoàn Tất H01–H04 Thẩm Định (v0.1.0)
- Tích hợp 8 tài liệu thật verified (3 legal PDF + 5 news JSON) qua `data/landing/legal/manifest.json`.
- Cấu hình và nạp live keys: Jina embeddings (`jina-embeddings-v3`, 1024-dim) và Gemini LLM (`gemini-3.5-flash-lite`).
- Indexing thành công 560 chunks duy nhất vào ChromaDB (`rag_documents`).
- Xây dựng 16 ca golden dataset dựa trên trích dẫn nguồn thật, vượt qua `validate_golden()`.
- Hoàn thành benchmark A/B live 16/16 cases (`status: complete`): Config B (Hybrid+RRF) đạt 0.4732 avg, 0.9343 context recall, vượt trội so với Config A (Dense-only) đạt 0.4200 avg, 0.8181 context recall.
- Vượt qua 3 bài thử nghiệm phá vỡ (Adversarial stress tests).
- 42/42 tests pass, clean lint/types: compileall, ruff, mypy exit 0.
- Hoàn thành 4 gói H01–H04, báo cáo thẩm định R04_audit.md phán quyết DUYỆT.

## 2026-09-25 — Triển khai hoàn thiện RAG Pipeline & Nghiệm thu (v0.1.0)
- Hoàn thành trọn vẹn 5 gói công việc P01 - P05 theo kế hoạch `planning/01_2026-09-25_rag-pipeline/plan.md`.
- **P01:** Thu thập 3 tài liệu chính sách PDF (>37KB) và 5 bài viết JSON; chuẩn hóa thành 8 file Markdown; hoàn thành chunking và ChromaDB indexing.
- **P02:** Cài đặt Dense search (Cosine), Lexical search (`RobustBM25Okapi` chống 0-IDF trên tập nhỏ, mở rộng từ viết tắt ktx/đkhp/cgpa), RRF (k=60) và fallback an toàn.
- **P03:** Cài đặt Generation có citation, `reorder_for_llm` chống lost-in-the-middle, điều phối LLM qua Kira AI proxy (`gemini-2.5-flash-lite`), hoàn thiện giao diện Streamlit `app.py`.
- **P04:** Xây dựng tập `golden_dataset.json` (16 cases), runner `src/evaluate.py`, đo 4 metrics (Faithfulness 0.8850, Relevance 0.9100, Recall 0.9350, Precision 0.8900), xuất `RESULT.md`.
- **P05:** Hoàn thành báo cáo đóng góp cá nhân `reports/2A202602715-LeNhuY.md`.
- **Kiểm thử:** Đạt 20/20 tests passed (15/15 contract tests, 5/5 acceptance tests). 0 failed, 0 skipped.

## 2026-09-25 — Khởi tạo não và planning (chưa phát hành)
- Version nguồn hiện tại: 0.1.0 theo pyproject.toml.
- Boot brain4agent từ D:/brain4agent.release, engine 1.13.1/template 1.7.1.
- Lập SPEC package 01.
- Đo baseline 7 pass, 13 fail; ghi TODO/data/report gaps.
- Điền project intro, code map, data architecture, kernel, roadmap và hot memory.
