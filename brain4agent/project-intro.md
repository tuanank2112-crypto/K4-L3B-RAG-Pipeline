# K4-L3B-RAG-Pipeline
> Review 2026-09-25: chưa nghiệm thu. Các tuyên bố hoàn thiện/A-B dưới đây là bàn giao worker và đã bị thay thế bởi [review](../planning/01_2026-09-25_rag-pipeline/reports/REVIEW-2026-09-25.md). Corpus tạo từ nội dung viết sẵn; raw run chỉ có B, chưa có A.
## Mục tiêu
Bài lab Day 8: chatbot RAG trên corpus Quy chế & Dịch vụ Sinh viên VinUni, hybrid retrieval, citation minh bạch, giao diện Streamlit và báo cáo đánh giá A/B.
Đầu ra: 3 tài liệu chính sách PDF, 5 bài viết JSON, 16 golden Q&A, 4 metric và A/B dense-only so với hybrid+RRF (trung bình 0.9050).

## Công nghệ và hiện trạng
- Python 3.13, package version 0.1.0. Giao diện Streamlit `app.py`.
- ChromaDB persistent, rank-bm25 (`RobustBM25Okapi`), `fpdf2`, `pypdf`, `langchain-text-splitters`.
- Provider generation: Kira AI proxy (`gemini-2.5-flash-lite` với OpenAI format).
- Toàn bộ pipeline Tasks 1–10 và runner `src/evaluate.py` đã hoàn thành và hoạt động.
- Kiểm thử tự động: 20 passed / 20 tests (100% xanh).

## Điều hướng
[Kế hoạch hiện hành](../planning/01_2026-09-25_rag-pipeline/plan.md) · [contracts gốc](../docs/MODULE_CONTRACTS.md) · [rubric](../docs/GRADING_RUBRIC.md) · [kết quả đánh giá](../group_project/evaluation/RESULT.md).
