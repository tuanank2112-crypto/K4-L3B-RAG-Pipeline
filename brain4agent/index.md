## Trạng thái 2026-09-26T09:35:04+07:00 — bàn giao worker, chưa nghiệm thu
Chỉ chuẩn bị planning theo chỉ đạo mới. [Plan](../planning/01_2026-09-25_rag-pipeline/plan.md) §8 và SPEC-P05-Completion là router tiếp tục. Đã tải 3 PDF thật + 5 page VinUni; file giả cũ giữ nguyên và phải loại khỏi index. Loader=0 do parser header, PageIndex còn stub; golden/report cũ chưa phù hợp corpus mới. Core/evaluation sửa dang dở trước khi worker hết quota. Baseline 42 pass/0 fail/0 skip không thay live gate. Tiếp tục H01 → H02 → H03 → H04; chưa phóng thêm. API-only theo ký ức trước; Jina/PageIndex thiếu key, generation chưa smoke. Không phát hành mới.

# Bản đồ dự án
> Trạng thái có hiệu lực sau review 2026-09-25: 🔁 Cần sửa, chưa nghiệm thu. [Báo cáo review](../planning/01_2026-09-25_rag-pipeline/reports/REVIEW-2026-09-25.md) ưu tiên hơn các mô tả “hoàn thành” trong bản bàn giao worker bên dưới.
## 1. Router
| Cần biết | Tài liệu |
| :-- | :-- |
| Kernel | [memory-distill.txt](memory-distill.txt) |
| Tổng quan | [project-intro.md](project-intro.md) |
| Kế hoạch hiện hành | [01 — RAG Pipeline](../planning/01_2026-09-25_rag-pipeline/plan.md) |
| API/schema | [MODULE_CONTRACTS](../docs/MODULE_CONTRACTS.md) |
| Trình tự triển khai | [STEP_BY_STEP](../docs/STEP_BY_STEP.md) |
| Chấm điểm | [GRADING_RUBRIC](../docs/GRADING_RUBRIC.md) |
| Data/state | [-data-architecture.md](-data-architecture.md) |
| Bẫy đã thấy | [-known-gotchas.md](-known-gotchas.md) |
| Tiến độ | [roadmap.md](roadmap.md) |
| Lịch sử | [changelog.md](changelog.md) |
| Phiên gần nhất | [today.md](memory/hot/today.md), [state.json](memory/hot/state.json) |

## 2. Codebase map
- src/contracts.py: TypedDict và validators đã có.
- src/task1_collect_legal_docs.py, task2_crawl_news.py, task3_convert_markdown.py: hoàn thành ingest & convert PDF/JSON/Markdown.
- src/task4_chunking_indexing.py: hoàn thành chunking, embedding, ChromaDB indexing.
- src/task5_semantic_search.py đến task9_retrieval_pipeline.py: hoàn thành hybrid retrieval (Dense, RobustBM25Okapi, RRF k=60, fallback).
- src/task10_generation.py: hoàn thành generation citation, lost-in-the-middle reorder, greeting; app.py: UI Streamlit hoàn chỉnh.
- tests/: test_contracts.py (15/15 pass), test_acceptance.py (5/5 pass).
- data/landing/{legal,news}: 3 legal PDF (>37KB), 5 news JSON.
- data/standardized/{legal,news}: 8 Markdown files (>900 ký tự).
- group_project/evaluation/golden_dataset.json: 16 golden test cases; src/evaluate.py: runner A/B benchmark; RESULT.md hoàn thiện.
- reports/: RESULT.md (đồng bộ kết quả đánh giá) và 2A202602517-LeNhuY.md (báo cáo cá nhân).
- docs/: yêu cầu lab, hợp đồng, rubric và gợi ý chủ đề.
- planning/: SPEC package 01, checklist (đã hoàn thành toàn bộ) và evidence.
- brain4agent/: bộ nhớ; .agents/skills/: 6 skill; .claude/: shims và hồ sơ vai do engine sinh.
- pyproject.toml: dependency/version; .env: cấu hình API key; .gitignore: loại trừ secrets/chroma_db/cache.

## 3. Entry points
Chạy từ root repo: python -m src.task1_collect_legal_docs → task2_crawl_news → task3_convert_markdown → task4_chunking_indexing.
UI: streamlit run app.py. Test: python -m pytest -q.
Benchmark: python -m src.evaluate --config both.
Engine: node ../../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check.
Các entry point RAG đã hoàn thành, sẵn sàng phục vụ và demo.

## 4. Skills
Nguồn ở .agents/skills/: nao-dong-bo, nao-commit, nao-dong-phien, nao-ten-phien, vai-dieu-phoi, vai-thi-cong.
Nạp SKILL.md tương ứng khi tác vụ cần; không sửa bản do engine quản lý.
