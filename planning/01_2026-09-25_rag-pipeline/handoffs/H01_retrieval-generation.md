Bạn là worker của repo này. THI CÔNG · tầng 🟠.
Bước 0: chạy node ../../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check.
Đọc kernel → index → specs/01-CONTRACTS.md → SPEC-P01/P02/P03 → TESTING-ACCEPTANCE.md → REVIEW-2026-09-25.md (mọi path tương đối package).
## Bối cảnh
Người dùng yêu cầu hoàn thành lab theo đề và SPEC hiện có; review chưa đạt.
## Phạm vi
Được sửa src/task4_chunking_indexing.py, task5_semantic_search.py, task8_pageindex_vectorless.py, task10_generation.py, tests/test_provider_regressions.py và report/evidence H01.
Cấm sửa file khác, corpus, .env, tests gốc; không commit/push, không upload live.
## Việc / xong khi
Sửa Gemini plural embeddings, validate vector count/dimension/finiteness; cache local sentence transformer nếu dùng.
Metadata title/source/url đúng header; chỉ URL HTTP(S). Giữ signatures.
Index phải hỗ trợ CHROMA_DIR/COLLECTION_NAME từ env để bảo toàn DB cũ; kiểm model/corpus mismatch rõ ràng, upsert theo batch.
Triển khai PageIndex thật theo SDK/docs chính thức (tự tra); timeout hữu hạn, mapping provenance, upload idempotent, failure graceful.
Generation kiểm citation/rỗng, refusal sạch không lộ error; shared helper generate_from_chunks(query,chunks) cho evaluation (lỗi provider có thể raise trong helper; wrapper safe).
Xong khi python -m pytest tests/test_contracts.py tests/test_provider_regressions.py -q exit 0; lưu cả lần đỏ trước fix.
## Luật
Tuân thủ SPEC đã nêu, không bịa live evidence; không chạm luật engine. Agent điều phối đang xử lý corpus/evaluation riêng.
## Tầng
P02/P03: 🟠; dùng model hiện tại, không cần spawn thêm.
## Report
reports/R01_retrieval-generation.md: dòng 1 khai vai/model/boot/hiểu việc, dòng 2 Handoff:, dòng 3 Base:, dòng 4 Head:; lệnh/exit/test count/diff stat/bảng gói-tầng-model/việc chưa làm; evidence/P02/*.txt output máy. Dòng cuối ✅/🔁/⛔.

## Tiếp tục 2026-09-26
Đọc SPEC-P05-Completion §1–6 trước ghi. API-only, không tải model local. Loader đọc header qua dòng trắng tới delimiter. Đo Base lúc nhận; không reset cây dirty. Worker report kết ⏳ chờ người duyệt, không tự nghiệm thu.
