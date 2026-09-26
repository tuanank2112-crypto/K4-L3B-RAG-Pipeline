# P02 — Retrieval và fallback
## Contract và thuật toán
Tasks 5–9 giữ [chữ ký](01-CONTRACTS.md).
Dense dùng embed_texts từ Task 4; score=1-cosine_distance.
BM25 dùng cùng corpus, lower-case/tokenization nhất quán lúc index và query.
RRF sum(1/(k+rank)), rank bắt đầu 1, gộp theo ID, top_k, tie ổn định theo ID.
retrieve lấy dense/sparse candidate top_k*2; use_reranking=True gọi RRF đúng một lần.
use_reranking=False trả dense giới hạn top_k khi không fallback; không dùng flag này đơn độc làm baseline A/B vì fallback vẫn có thể chạy.
Best dense=max(score) hoặc 0 nếu rỗng; chỉ thử PageIndex khi best_dense < threshold.
PageIndex có kết quả hợp lệ thì trả; lỗi/rỗng thì trả hybrid (hoặc dense trong nhánh không reranking).
upload_documents lưu mapping nguồn→document ID vào pageindex_doc_ids.json đã ignore; kiểm SDK thật trước adapter.
Kết quả fallback có metadata.chunk_index, provenance và retrieval_method=pageindex; nếu không có score dùng giá trị giảm theo rank.

## Bắt buộc / vùng cấm
BẮT BUỘC timeout hữu hạn, không làm UI crash khi dịch vụ fallback lỗi.
CẤM so RRF score với threshold; CẤM fuse lại ở generation/UI.
CẤM đổi schema/chữ ký để bỏ requirement PageIndex.
Threshold 0.3 chỉ là mặc định skeleton; calibration tối thiểu 5 query trong domain và 5 ngoài domain, tách khỏi golden test.

## Lỗi và caller
| Lỗi | Hành vi |
| :-- | :-- |
| PageIndex thiếu key/timeout/response hỏng | Giữ kết quả retrieval hiện có; log đã che secrets |
| Dense hỏng khi BM25 còn dùng được | Trả kết quả BM25 qua fusion; thử fallback nếu có cấu hình |
| Cả hai retrieval rỗng/lỗi | Thử fallback; cuối cùng [] để generation từ chối |
| Input trắng/top_k ≤0 | [] và không gọi provider |

## Nghiệm thu
python -m pytest tests/test_contracts.py -q -k "semantic or lexical or rrf or retrieve" → exit 0.
Thêm mock tests: RRF call count=1; dense cao không gọi fallback; dense thấp gọi fallback; provider lỗi vẫn trả hợp lệ.
PageIndex smoke thật và threshold calibration ghi evidence/P02/*.txt; mock không thay cho chứng minh dịch vụ thật.
