# P01 — Data và indexing
## Phạm vi và contract
Sửa Tasks 1–4; corpus ở data/landing/{legal,news}, Markdown ở data/standardized/{legal,news}.
Áp dụng [schema/chữ ký](01-CONTRACTS.md). Chốt chủ đề trước thu thập; nguồn có URL, title, doc_type và ngày crawl.
ID document = đường tương đối chuẩn hóa trong standardized; chunk ID = document ID + ::chunk-N. Chạy lại cùng đầu vào phải cho cùng ID.
Chunk mặc định 500 ký tự, overlap 50 theo code; thay đổi phải ghi config để tái lập.
Chroma persistent ở chroma_db, collection rag_documents, cosine; embed_texts dùng cùng model/dimension ở ingest và query.
BM25 phải nạp cùng chunks sau khi khởi động tiến trình mới; không chỉ dựa vào biến CORPUS rỗng của skeleton.
Metadata url=null phải được mã hóa phù hợp storage và khôi phục đúng contract khi đọc.

## Bắt buộc / vùng cấm
BẮT BUỘC ≥3 legal mỗi file >1024 bytes; ≥5 news JSON đủ metadata; ≥3+5 Markdown mỗi file ≥200 ký tự.
Dùng upsert và kiểm tra số ID sau hai lần index. Không tự xóa corpus hoặc collection cũ khi đổi model.
CẤM dùng tài liệu giả để đạt số lượng; CẤM coi embedding model đã tải/cài sẵn.
Chỉ hỗ trợ provider thực sự được cấu hình; chưa cấu hình thì trả lỗi rõ.

## Lỗi và caller
| Lỗi | Hành vi |
| :-- | :-- |
| Download/crawl timeout | Retry hữu hạn, ghi URL lỗi và tiếp tục nguồn độc lập |
| PDF scan/convert rỗng | Báo cần nguồn thay thế/OCR; không index rỗng |
| Metadata thiếu | Không đưa vào corpus đạt nghiệm thu |
| Collection sai dimension | Dừng, bảo toàn bản cũ; tạo collection thử nghiệm riêng |

## Nghiệm thu
Chạy lần lượt python -m src.task1_collect_legal_docs, task2_crawl_news, task3_convert_markdown, task4_chunking_indexing.
python -m pytest tests/test_acceptance.py -q -k "corpus or standardized" phải exit 0.
Ghi count ID trước/sau lần index thứ hai: bằng nhau, duplicate=0; xác minh query tiến trình mới có cả dense/BM25 trên cùng ID set.
Chưa chạy ingest thật trong phiên planning; bằng chứng để ở evidence/P01/*.txt khi thi công.
