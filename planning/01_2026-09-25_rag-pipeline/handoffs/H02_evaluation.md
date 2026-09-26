Bạn là worker của repo này. THI CÔNG · tầng 🟠.
Bước 0: chạy node ../../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check.
Đọc kernel → index → specs/01-CONTRACTS.md → SPEC-P04-Evaluation.md → TESTING-ACCEPTANCE.md → REVIEW-2026-09-25.md (path tương đối package).
## Bối cảnh
Người dùng yêu cầu hoàn thành lab theo SPEC; evaluation hiện bịa điểm thiếu nhánh và nuốt lỗi dense.
## Phạm vi
Chỉ src/evaluate.py, tests/test_evaluation_regressions.py, report/evidence H02. Không sửa golden/corpus/reports RESULT/.env/tests gốc.
## Việc / xong khi
Loại mọi metric/conclusion/bonus điền sẵn; generate_report(None, B) ghi chưa đo A, không delta.
Provider lỗi => case status error + metrics null, run incomplete + exit nonzero, không mean bỏ lỗi để tuyên bố complete. Không lộ secrets/error raw.
Giữ 4 metric token heuristic với công thức minh bạch (không cộng điểm nền), ghi rõ không phải semantic RAGAS. Cùng prompt/generator A/B, fallback tắt.
Ghi fingerprints corpus, golden, embedding/model, generation/prompt, SDK versions, top_k, raw sources và câu trả lời. Validate golden nguồn trước live.
Worker H01 sẽ cung cấp task10_generation.generate_from_chunks(query,chunks) shared helper; dùng helper, propagate lỗi để raw artifact ghi incomplete.
Report đủ headings acceptance, worst performers từ case thật, nhận xét tùy delta, hạn chế/khuyến nghị không bịa nguyên nhân/bonus.
Xong khi python -m pytest tests/test_evaluation_regressions.py -q exit 0; lưu test đỏ trước sửa. Chưa chạy live evaluation (root làm sau corpus/index).
## Luật
Không commit/push. Giữ signatures cũ khi có thể. Không sửa luật/plan ngoài phạm vi.
## Tầng
P04: 🟠, model hiện tại, không cần spawn thêm.
## Report
reports/R02_evaluation.md dòng 1 khai vai/model/boot/hiểu việc; dòng 2 Handoff:, 3 Base:, 4 Head:; lệnh/exit/tests/diff stat/SHA/bảng gói-tầng-model/việc chưa làm; evidence/P04/*.txt output máy. Dòng cuối ✅/🔁/⛔.

## Tiếp tục 2026-09-26
Đọc SPEC-P05-Completion §1–6 trước ghi. API-only, không tải model local. Loader đọc header qua dòng trắng tới delimiter. Đo Base lúc nhận; không reset cây dirty. Worker report kết ⏳ chờ người duyệt, không tự nghiệm thu.
