Bạn là worker của repo này. THẨM ĐỊNH · tầng 🔴, phiên độc lập.
Bước 0: chạy node ../../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check.
Đọc brain4agent/memory-distill.txt → index.md → README.md → docs/MODULE_CONTRACTS.md, GRADING_RUBRIC.md → toàn bộ specs/ của planning/01_2026-09-25_rag-pipeline → code/tests/corpus thật.
## Bối cảnh
Đánh giá lab theo đề sau worker thi công. Không kế thừa chat, không đọc H01–H03 hoặc R01–R03 hay lời kể worker.
## Phạm vi
Chỉ đọc source/corpus/config (không in secrets), chạy phép đo; được ghi reports/R04_audit.md và evidence/audit/*.txt. Cấm sửa mã, tests gốc, DB/corpus thật, gọi upload/deploy/push.
## Việc và xong khi
Đo lại từng gate SPEC-P05-Completion §6, kiểm provenance và các report RESULT so raw, golden so nguồn; xác minh 4 metric đúng công thức và limitations.
Tự thiết kế ≥3 phá: metadata/header không khớp; dense timeout trong A/B; citation giả hoặc PageIndex mapping sai. Chạy cô lập trên tmp_path/bản sao, chứng minh test phát hiện hệ hỏng.
Xong khi R04 ghi đủ lệnh/exit/count/phạm vi/fingerprint và verdict từng gate; không đạt thì chỉ rõ file/dòng/mục SPEC. Thiếu live evidence là chưa đạt, không gán pass nhờ mock.
## Luật
Giữ working tree dirty từ trước, không git checkout/reset/clean. Hai phép đo mâu thuẫn hoặc lỗi lặp 2 lần thì nêu cần phân xử. Không tự đóng plan/phát hành.
## Tầng
Thẩm định độc lập 🔴; dùng họ model khác người thi công khi khả dụng; ghi họ/model thật.
## Report
R04 dòng 1 khai vai/model/boot/hiểu việc; dòng 2 Handoff:, 3 Base:, 4 Head: tự đo. Chỉ số đo, test total/pass/fail/skip, diff stat + SHA, bảng phân công, chưa làm/lý do/câu hỏi; evidence output máy. Dòng cuối ✅ DUYỆT / 🔁 SỬA: mục cụ thể / ⛔ DỪNG: lý do.
