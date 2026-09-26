Bạn là worker của repo này. THI CÔNG · tầng 🟠, tài liệu 🟢.
Bước 0: chạy node ../../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check.
Đọc brain4agent/memory-distill.txt → index.md → docs/MODULE_CONTRACTS.md → package specs/00-ARCHITECTURE.md → 01-CONTRACTS.md → SPEC-P01..P05 → OPERATIONS.md → TESTING-ACCEPTANCE.md.
## Bối cảnh
Package = planning/01_2026-09-25_rag-pipeline. Người dùng chỉ yêu cầu chuẩn bị planning; handoff này chờ worker nhận. H01/H02 phải xong trước bước tích hợp.
## Phạm vi
Được ghi src/task1..3, task6..7, task9, app.py, tests/test_data_regressions.py, tests/test_ui_regressions.py, data/landing và standardized nguồn thật, golden_dataset.json, evaluation/runs, hai RESULT.md, README.md, pyproject.toml, .env.example, reports/2A202602715-LeNhuY.md, docs/, brain4agent/, checklist plan và evidence/P01,P03,P05, report R03.
Không chạm luật engine, tests gốc, code H01/H02; cần sửa giao diện giữa gói thì báo mục SPEC và giao lại người phụ trách. Không xóa dữ liệu cũ, sửa .env, mua credit, deploy/push/commit.
## Việc và xong khi
Thực hiện SPEC-P05-Completion §2–6; đầu vào nguồn thật có sẵn nhưng phải kiểm hash/parser/edition. Không dùng golden giả cũ.
Xong khi các lệnh §6 exit 0; corpus verified đúng 8; 2 lần index unique ID/count bằng nhau; 10 calibration query riêng; python -m src.evaluate --config both có ≥15 case/config complete và 4 metric/raw/fingerprint; UI 3 tình huống không crash.
Nếu thiếu key/provider: hoàn tất offline, raw/status chưa đo và gate live mở; không gọi đây là lab hoàn thành.
## Luật
Đo git rev-parse HEAD và snapshot/hash file trong phạm vi trước ghi; cây đã dirty/untracked, không reset. Handoff trỏ SPEC, không tự thay requirement. Báo cáo cá nhân chỉ bản nháp cần học viên xác nhận ownership.
## Tầng
Data/index/calibration/evaluation/UI 🟠; docs/não 🟢. Phân tầng và bảng model thực dùng; nếu không có tầng phù hợp dùng tầng cao hơn, ghi lý do.
## Report
reports/R03_completion.md dòng 1 khai vai/model/boot/hiểu việc; dòng 2 Handoff:, 3 Base: đo thực, 4 Head: đo thực và ghi working tree khi chưa commit. Gồm commands/exit/tests/diff stat/SHA/bảng phân công/giới hạn/câu hỏi, link evidence máy. Kết ⏳ chờ reviewer; người duyệt đặt ✅/🔁/⛔, không tự đóng plan.
