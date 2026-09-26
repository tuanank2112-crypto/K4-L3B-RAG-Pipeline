## Trạng thái 2026-09-26T09:35:04+07:00 — bàn giao worker, chưa nghiệm thu
Chỉ chuẩn bị planning theo chỉ đạo mới. [Plan](../planning/01_2026-09-25_rag-pipeline/plan.md) §8 và SPEC-P05-Completion là router tiếp tục. Đã tải 3 PDF thật + 5 page VinUni; file giả cũ giữ nguyên và phải loại khỏi index. Loader=0 do parser header, PageIndex còn stub; golden/report cũ chưa phù hợp corpus mới. Core/evaluation sửa dang dở trước khi worker hết quota. Baseline 42 pass/0 fail/0 skip không thay live gate. Tiếp tục H01 → H02 → H03 → H04; chưa phóng thêm. API-only theo ký ức trước; Jina/PageIndex thiếu key, generation chưa smoke. Không phát hành mới.

# Kiến trúc dữ liệu
> Review 2026-09-25: số lượng file tồn tại nhưng chưa có provenance nguồn thật; PageIndex còn stub; benchmark A chưa chạy. Không coi luồng và trạng thái bên dưới là đã nghiệm thu. Xem [review](../planning/01_2026-09-25_rag-pipeline/reports/REVIEW-2026-09-25.md).
## Hiện trạng
- Corpus đã nạp đủ: 3 legal PDF (>37KB), 5 news JSON; 8 file Markdown chuẩn hóa (>900 ký tự).
- golden_dataset.json có 16 ca kiểm thử có ground truth hoàn chỉnh.
- ChromaDB persistent tại chroma_db/ (đã được .gitignore bảo vệ).
- BM25 tự động nạp chunks từ standardized documents qua RobustBM25Okapi với Lucene smoothing.

## Luồng dữ liệu thực tế
landing/legal (PDF) + landing/news (JSON) → standardized/legal|news (Markdown) → Document → Chunk (500 chars, overlap 50) → embedding → ChromaDB cosine.
BM25 dùng cùng corpus chunks và ID; tự động nạp lại khi khởi động tiến trình mới.
Dense + BM25 → RRF (k=60) một lần → kiểm tra fallback nếu có cấu hình → generation có citation + lost-in-the-middle reorder → session_state Streamlit.

## Lưu trữ và ranh giới
- chroma_db/ là cache persistent cục bộ, đã thêm vào .gitignore.
- pageindex_doc_ids.json, pageindex_pdfs/ và .env đã được ignore.
- Document metadata bảo toàn source/title/doc_type/url; chunk bổ sung chunk_index.
- Đích evaluation: group_project/evaluation/RESULT.md (đã hoàn thiện không còn TODO) và đồng bộ reports/RESULT.md.
- [Contract chi tiết](../planning/01_2026-09-25_rag-pipeline/specs/01-CONTRACTS.md).
