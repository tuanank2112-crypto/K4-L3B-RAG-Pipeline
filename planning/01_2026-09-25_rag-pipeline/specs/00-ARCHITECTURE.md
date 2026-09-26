# Kiến trúc
## Mục tiêu và phạm vi
Hoàn thiện chatbot lab trả lời từ corpus do nhóm chọn: ≥3 tài liệu chính sách và ≥5 bài viết; hybrid retrieval, fallback, citation, UI và evaluation.
Đọc [contracts](01-CONTRACTS.md), rồi SPEC của gói được giao, cuối cùng [testing](TESTING-ACCEPTANCE.md).

## Luồng và contract
Task 1–2 → data/landing → Task 3 → data/standardized → Task 4 → chunks/Chroma → Tasks 5–7 → Task 9 (Task 8 fallback) → Task 10 → app.py.
Document → Chunk/EmbeddedChunk → SearchResult → GenerationResult đúng [contracts gốc](../../../docs/MODULE_CONTRACTS.md).
Python ≥3.10,<3.14; Streamlit; Chroma; BM25; provider theo .env.example. Chưa có backend HTTP riêng.

## Bất biến và vùng cấm
BẮT BUỘC giữ stable IDs, provenance và shared embedding; RRF chỉ một lần; threshold trên cosine gốc.
CẤM sửa luật engine, thay public signatures để né test, bịa corpus/metrics hoặc commit secrets.
Không thêm microservices, database khác, auth, deployment hay bonus trước core vì không cần cho nghiệm thu lab.
Không sửa D:/brain4agent.release. Chỉ engine quản lý AGENTS/CLAUDE, marker và skill được đồng bộ.

## Lỗi và caller
| Lỗi | Hành vi |
| :-- | :-- |
| Input/schema sai | Fail rõ ở ingest; không index dữ liệu sai |
| Nguồn rỗng/không đủ | Báo thiếu, giữ gate corpus chưa đạt |
| Provider không sẵn sàng | Retrieval/generation xử lý theo SPEC tương ứng |
| Thiếu chủ đề/quyền dịch vụ | Làm phần offline độc lập, ghi đầu vào còn thiếu |

## Nghiệm thu
[Baseline](../evidence/P00/baseline-tests.txt): 7 pass / 13 fail; đây là hiện trạng khung lab.
Thành công sản phẩm phải qua mọi gate local trong [testing](TESTING-ACCEPTANCE.md); chưa có bằng chứng end-to-end.
