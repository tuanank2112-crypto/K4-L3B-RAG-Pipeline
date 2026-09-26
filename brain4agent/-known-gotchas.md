## Trạng thái 2026-09-26T09:35:04+07:00 — bàn giao worker, chưa nghiệm thu
Chỉ chuẩn bị planning theo chỉ đạo mới. [Plan](../planning/01_2026-09-25_rag-pipeline/plan.md) §8 và SPEC-P05-Completion là router tiếp tục. Đã tải 3 PDF thật + 5 page VinUni; file giả cũ giữ nguyên và phải loại khỏi index. Loader=0 do parser header, PageIndex còn stub; golden/report cũ chưa phù hợp corpus mới. Core/evaluation sửa dang dở trước khi worker hết quota. Baseline 42 pass/0 fail/0 skip không thay live gate. Tiếp tục H01 → H02 → H03 → H04; chưa phóng thêm. API-only theo ký ức trước; Jina/PageIndex thiếu key, generation chưa smoke. Không phát hành mới.

# Những điểm cần lưu ý
## Lỗi xác nhận qua review 2026-09-25 — chưa sửa
- Corpus là nội dung viết sẵn được xuất PDF/JSON; chưa có bằng chứng thu thập nguồn VinUni thật.
- evaluate.generate_report điền điểm mặc định khi thiếu config. Raw run có A=null; không có A/B hợp lệ.
- Benchmark nuốt lỗi dense thành [] rồi tính metric, khiến BM25-only mang nhãn hybrid.
- Generation không kiểm nhãn citation hoặc answer rỗng; cả ba trường hợp lỗi đều vượt qua 20 tests hiện có.
- PageIndex luôn trả []; upload không upload dù đã cấu hình key.
- Gemini embedding đọc result.embedding thay vì response.embeddings; probe SDK xác nhận AttributeError.
- metadata.url của legal là filename.pdf khiến UI tạo liên kết nguồn sai.
- [Review + bằng chứng](../planning/01_2026-09-25_rag-pipeline/reports/REVIEW-2026-09-25.md). Các ghi chú worker dưới đây không thay thế các hạn chế này.

## Ghi chú bàn giao worker trước review
- Baseline 2026-09-25 lúc khởi đầu: 20 tests, 7 pass, 13 fail; sau triển khai: 20 passed / 20 tests (100% xanh).
- **BM25 0-IDF trên corpus nhỏ:** ATIRE BM25Okapi gốc trả idf = 0 khi một từ xuất hiện ở đúng 50% số document (ví dụ 1/2 docs). Đã giải quyết bằng `RobustBM25Okapi` với công thức làm mịn của Lucene `math.log(1.0 + (N - n + 0.5) / (n + 0.5))`.
- **Tách từ tiếng Việt và viết tắt:** Truy vấn tiếng Việt có dấu câu (`?`, `.`) và viết tắt sinh viên (`ktx`, `đkhp`, `cgpa`) làm BM25 thuần trượt kết quả. Đã bổ sung `tokenize_text` bóc dấu câu và `expand_query` mở rộng từ viết tắt.
- **Xử lý thiếu Embedding API key:** Khi chưa có key embedding bên ngoài, pipeline tự động bọc try/except quanh `semantic_search` để chuyển tiếp mượt mà sang `lexical_search` mà không làm sập giao diện hay ném unhandled exception.
- **Safe Refusal & Chào hỏi:** Safe Refusal từ chối các câu không có căn cứ, nhưng cần phân biệt với câu chào hỏi (`chào bạn`, `hello`) bằng `is_greeting` để bot giới thiệu danh mục chức năng thân thiện.
- **Windows Console cp1252:** Khi chạy lệnh in tiếng Việt trên console Windows, cần gán `$env:PYTHONIOENCODING="utf-8"` hoặc xử lý encode UTF-8 an toàn để tránh `UnicodeEncodeError`.
- **Envelope contract:** Task 10 envelope `retrieval_source` chỉ chấp nhận `hybrid`, `pageindex`, hoặc `none` (không được trả `dense` hoặc `bm25` ở tầng vỏ).
- **Chroma metadata boundary:** URL rỗng được lưu dạng `""` trong ChromaDB để tránh lỗi kiểu dữ liệu và được khôi phục thành `None` khi truy vấn theo schema.
- **Result destination:** Đích của báo cáo nghiệm thu là `group_project/evaluation/RESULT.md`, được đồng bộ với template `reports/RESULT.md`.
