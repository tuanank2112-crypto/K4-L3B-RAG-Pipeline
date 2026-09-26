# P04 — Evaluation và báo cáo
## Contract
golden_dataset.json tại group_project/evaluation là list ≥15 rows theo [schema](01-CONTRACTS.md), dựa trên nguồn thật, không lấy đáp án mô hình làm ground truth.
Tạo runner src/evaluate.py (đề xuất mới), chạy python -m src.evaluate --config both.
A=dense-only trực tiếp semantic_search; B=hybrid+RRF. Cố định corpus, top_k, embedding/generator/evaluator, prompt, seed nếu hỗ trợ.
Trong phép đo A/B chính tắt PageIndex cả hai nhánh để chỉ đổi retrieval strategy; kiểm fallback bằng smoke riêng.
Dùng cùng logic format/generation nội bộ; giữ API công khai generate_with_citation(query, top_k).
Đo faithfulness, answer relevance, context recall, context precision cho từng câu và aggregate; thêm latency/cost nếu đo được.
RESULT.md đích: group_project/evaluation/RESULT.md; lấy template reports/RESULT.md, không sửa test né đường dẫn.
Đầu ra runner: group_project/evaluation/runs/<run-id>/results.json chứa config, corpus ID, từng case, metric và lỗi.

## Bắt buộc / vùng cấm
BẮT BUỘC báo worst performers, nguyên nhân, khuyến nghị và Delta B−A; kết quả có ngày, model, version, corpus commit/hash.
Không cam kết hybrid thắng; báo đúng số đo. Không đưa calibration set vào test set.
CẤM điền số liệu dự đoán; không tự mua credit hoặc ghi secrets trong evidence.
Tên model và phiên bản SDK kiểm thực tế ở lúc thi công; SPEC không giả định API cụ thể.

## Lỗi và caller
| Lỗi | Hành vi |
| :-- | :-- |
| Golden JSON rỗng/sai hoặc thiếu nguồn | Runner dừng trước gọi API |
| Evaluator timeout/quota | Ghi case lỗi, retry hữu hạn; báo run chưa đủ, không tính như 0 |
| Hai config khác corpus/prompt/model | Dừng A/B, chưa công bố so sánh |
| Không có ngân sách/key | Offline validation vẫn làm được; live evaluation chờ cấu hình |

## Nghiệm thu
python -m pytest tests/test_acceptance.py -q → exit 0.
python -m src.evaluate --config both → exit 0 với ≥15 cases ×2 configs, 4 metric có giá trị thật và raw output truy vết.
Report không còn TODO, đủ Overall scores, A/B comparison, Worst performers, Recommendations.
Lưu evidence/P04/*.txt; README sửa các link báo cáo hiện lệch. Báo cáo cá nhân lấy reports/INDIVIDUAL_REPORT.md, cần thông tin thành viên thật.
