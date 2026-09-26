# Kiểm thử và nghiệm thu
## Contract bằng chứng
Mỗi gate phải có lệnh, exit code, count pass/fail/skip, môi trường và output thật ở evidence/<gói>/*.txt.
Baseline 2026-09-25: python -m pytest -q -p no:cacheprovider → exit 1; 20 total, 7 pass, 13 fail, 0 skip.
Xem [output baseline](../evidence/P00/baseline-tests.txt). Test đỏ là khung chưa triển khai, không phải lỗi boot não.

## Ma trận
| Gate | Lệnh / phép đo | Điều kiện |
| :-- | :-- | :-- |
| Brain | node ../../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check | exit 0 |
| Offline contracts | python -m pytest tests/test_contracts.py -q | 0 fail/skip, không network |
| Corpus/report | python -m pytest tests/test_acceptance.py -q | ≥3 legal, ≥5 news, Markdown, ≥15 golden, report đủ |
| Toàn bộ | python -m pytest -q | exit 0, không giảm số test gốc |
| Index idempotency | Chạy Task 4 hai lần cùng đầu vào | count ID giữ nguyên, duplicate=0 |
| Citation | Mock reorder/citation và smoke câu có nguồn | Mọi nhãn ánh xạ đúng ID; đọc đối chiếu nội dung |
| Provider/fallback | Mock lỗi + smoke cấu hình thật | Không crash; refusal/hybrid đúng nhánh |
| A/B | python -m src.evaluate --config both (runner sẽ tạo) | 2 config cùng corpus, ≥15 case/config, 4 metric |
| UI | python -m streamlit run app.py | Câu có nguồn, ngoài domain, provider lỗi đều xử lý được |

## Bắt buộc / vùng cấm
Không gọi network/model thật trong contract tests. Test sinh mới phải đo hành vi, không chép lại implementation.
Thêm các ca: empty query/top_k, ties/duplicates, score NaN, metadata URL null, persistent BM25 sau restart, citation sau reorder, provider timeout.
CẤM sửa số lượng/cấu trúc test gốc để làm xanh; CẤM tuyên bố mock là live smoke.
Môi trường nghiệm thu là local; deploy chưa thuộc kế hoạch.

## Lỗi và caller
| Loại | Xử lý |
| :-- | :-- |
| Test fail hành vi | Giữ gate chưa đạt, sửa gói liên quan |
| Thiếu dependency/key/corpus | Ghi blocked theo môi trường, không ghi pass |
| A/B thiếu case hoặc metric | Chưa đạt evaluation; không lấy mean bỏ lỗi mà không khai báo |
| Tài liệu link chết/state sai | Sửa router/state trước bàn giao |

## Trạng thái
P00 chỉ nghiệm thu cấu trúc não/planning. Các gate sản phẩm còn mở; chưa có kết quả RAG live.
