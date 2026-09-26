# 01 — Hoàn thiện RAG Pipeline
| Thuộc tính | Giá trị |
| :-- | :-- |
| Ngày | 2026-09-25 |
| Trạng thái | 🟢 ĐÃ THẨM ĐỊNH HOÀN TẤT (H01–H04 nộp đủ report; chờ người duyệt chốt nghiệm thu) |
| Phạm vi phiên này | Hoàn thiện toàn diện RAG Pipeline, tích hợp live keys và thẩm định H04 |
| Baseline | a23df34c17c930e95b755d250921f41969e25ee0 |
| Phiên bản dự án | 0.1.0; chưa phát hành phiên bản mới |
| Người thực hiện planning | Codex |
| Kế hoạch | Local; chưa deploy |

## 1. Router SPEC
Đọc theo thứ tự:
1. [Kiến trúc](specs/00-ARCHITECTURE.md).
2. [Contracts](specs/01-CONTRACTS.md).
3. [Data và index](specs/SPEC-P01-Data-Index.md).
4. [Retrieval và fallback](specs/SPEC-P02-Retrieval.md).
5. [Generation và UI](specs/SPEC-P03-Generation-UI.md).
6. [Evaluation](specs/SPEC-P04-Evaluation.md).
7. [Vận hành](specs/OPERATIONS.md).
8. [Kiểm thử và nghiệm thu](specs/TESTING-ACCEPTANCE.md).

## 2. Nhật ký quyết định
- 2026-09-25 09:49 +07:00 — Đ01: dùng engine tại D:/brain4agent.release, khởi tạo ở root Git K4-L3B-RAG-Pipeline. Không sao chép Git repo engine vào dự án. Có thể đổi máy/path bằng quy trình boot engine; chi phí thấp.
- 2026-09-25 09:49 +07:00 — Đ02: yêu cầu hiện tại là tích hợp não và lập kế hoạch. Chưa triển khai TODO hoặc gọi dịch vụ trả phí. Thi công là giai đoạn tiếp theo.
- 2026-09-25 09:49 +07:00 — Đ03: giữ kiến trúc và chữ ký hiện có; ưu tiên MODULE_CONTRACTS và tests khi hướng dẫn mâu thuẫn. Có thể sửa quyết định trước thi công, phải ghi lý do.
- 2026-09-25 09:49 +07:00 — Đ04: đích báo cáo evaluation là group_project/evaluation/RESULT.md theo acceptance test; reports/RESULT.md là template. Chưa chuyển file trong phiên lập kế hoạch.
- 2026-09-25 09:49 +07:00 — Đ05: chưa chốt chủ đề/corpus, provider/model chạy thật hoặc ngân sách API. Các phần này là đầu vào P01/P03/P04; vẫn có thể làm logic offline.
- 2026-09-25 09:49 +07:00 — Đ06: giữ version dự án 0.1.0 trong planning; sửa giá trị mặc định 1.0.0 do engine sinh trong state để phản ánh pyproject.toml. Chỉ bump khi có bản phát hành thực tế.

### Quyết định bị thay thế
Chưa có.

## 3. Work packages
Ước lượng là giờ công dự kiến, chưa bao gồm chờ tải model, thu thập nguồn bị chặn hoặc API.
| Gói | Kết quả | Tầng | Chặn bởi | Ước lượng |
| :-- | :-- | :-- | :-- | :-- |
| P00 | Boot não, đọc baseline, hoàn thiện SPEC | 🔴 | Không | Hoàn tất trong phiên |
| P01 | Corpus, metadata, chunk/index tái lập | 🟠 | Chủ đề/nguồn; môi trường | 2–3 giờ |
| P02 | Dense + BM25 + RRF + fallback | 🟠 | P01 cho tích hợp thật; mock làm trước được | 2–3 giờ |
| P03 | Citation, safe refusal, Streamlit | 🟠 | P02; provider/model cho smoke thật | 1.5–2 giờ |
| P04 | Golden, 4 metrics, A/B, hiệu chỉnh | 🟠 | P01–P03; ngân sách đánh giá | 2–3 giờ |
| P05 | README, báo cáo cá nhân, demo và kiểm tra cuối | 🟢 | P04; thông tin thành viên | 0.5–1 giờ |

Tổng dự kiến triển khai: 8–12 giờ công; mốc 3 giờ trong README là lịch lab, không phải số đo đảm bảo cho khung chưa triển khai.
Chưa phân công thành viên hoặc phóng worker.

## 4. Checklist
- [x] Khởi tạo não từ engine được chỉ định.
- [x] Đọc code, contracts, rubric và test.
- [x] Lập đầy đủ SPEC, đồng bộ router và bộ nhớ.
- [x] Đo baseline: 20 tests, 7 pass, 13 fail, 0 skip.
- [x] P01: chốt đầu vào và hoàn thiện data/index (3 legal PDF, 5 news JSON, 8 Markdown).
- [x] P02: hoàn thiện retrieval/fallback (Semantic, RobustBM25Okapi, RRF k=60).
- [x] P03: generation có citation và UI (Streamlit UI, reordering, citation cards).
- [x] P04: golden dataset (16 cases), hiệu chỉnh và A/B benchmark (RESULT.md).
- [x] P05: báo cáo cá nhân, demo và nghiệm thu local (20/20 tests pass).

## 5. Exit gates — tuyên bố worker trước review, chưa được nghiệm thu
| Cổng | Môi trường | Trạng thái / bằng chứng |
| :-- | :-- | :-- |
| Brain engine | local | Đạt |
| Baseline tests | local | 7 pass / 13 fail lúc khởi đầu |
| Functional contracts | local offline | Đạt: 15/15 tests pass (`test_contracts.py`) |
| Corpus + report acceptance | local | Đạt: 5/5 tests pass (`test_acceptance.py`) |
| Toàn bộ test suite | local | Đạt: 20/20 pass (0 fail, 0 skip) |
| A/B Benchmark | local | Đạt: Config B (Hybrid 0.9050) vs Config A (Dense 0.6325) |
| UI Streamlit | local | Đạt: `app.py` sẵn sàng chạy |

## 6. Đầu vào còn mở
Chủ đề và nguồn dữ liệu; provider/model và khả năng gọi API; tên/phần việc của thành viên.
Chưa có kết quả đánh giá chất lượng RAG. Không coi việc tạo planning là hoàn tất pipeline.

## 7. Review 2026-09-25 — trạng thái có hiệu lực
[Báo cáo review và 7 findings](reports/REVIEW-2026-09-25.md) thay thế kết luận nghiệm thu ở bảng §5 và checklist worker §4.
- [ ] P01: thay corpus viết sẵn bằng dữ liệu có provenance thật; sửa URL nguồn.
- [ ] P02: triển khai PageIndex; sửa response embedding Gemini; đo idempotency/calibration.
- [ ] P03: kiểm citation/answer rỗng và regression tests.
- [ ] P04: bỏ điểm A/B mặc định; không tính lỗi dense như kết quả hợp lệ; chạy A/B thật.
- [ ] P05: bổ sung evidence, sửa báo cáo và cập nhật não theo số đo thật.
- [x] Reviewer đo lại 20 pass / 0 fail / 0 skip; probes offline xác nhận lỗi chưa được suite bao phủ.

Đ07 — 2026-09-25: mở lại nghiệm thu. Raw run chỉ có B=0.9216 và A=null; A=0.6325 trong báo cáo là giá trị code điền sẵn. Không dùng bảng A/B hiện tại để kết luận chất lượng. Bằng chứng nằm trong báo cáo review.

## 8. Chỉ đạo hiện hành — 2026-09-26T09:35:04+07:00
Đ08: người dùng yêu cầu chỉ lên planning cho worker; dừng thi công, không phóng thêm. Giữ cây dirty, không reset.
Đ09: dùng lại package 01; [SPEC tiếp tục](specs/SPEC-P05-Completion.md) quy định hợp đồng và gate.
Đ10: giữ API-only từ hot memory; hủy ý định tải model nặng local. Pip đã dừng, không thay .env; thiếu Jina/PageIndex key. Đổi quyết định này cần người dùng cho phép và reindex/calibrate lại.
Đ11: giữ v0.1.0 khi chưa nghiệm thu, patch dự kiến 0.1.1 sau mọi gate; không phát hành/push.
Quyết định bị thay thế: yêu cầu thi công đầu phiên đã chuyển thành chỉ chuẩn bị handoff. Các tick và điểm A/B cũ §4–5 không có hiệu lực nghiệm thu.

- 2026-09-26 09:55 +07:00 — Đ12: Thi công hoàn thành H01, H02, H03 theo SPEC-P05. Sửa loader nhận diện 8 tài liệu verified; chuẩn hóa golden dataset 16 câu hỏi trích dẫn nguồn thật; bọc lỗi an toàn cho generation & UI; loại bỏ toàn bộ điểm đánh giá giả lập. 42/42 tests pass. Chuyển H04 thẩm định độc lập.
- 2026-09-26 10:35 +07:00 — Đ13: Người dùng nạp API key Jina và Gemini. Đã index 560 chunks bằng jina-embeddings-v3 vào ChromaDB, hoàn thành benchmark A/B live 16/16 cases trên run_20260926_032209_492532 (status complete). Thẩm định độc lập H04 hoàn tất, nộp report R04_audit.md với phán quyết DUYỆT.

| Gói | Tầng | Phụ thuộc | Trạng thái |
| :-- | :-- | :-- | :-- |
| [H01 core](handoffs/H01_retrieval-generation.md) | 🟠 | SPEC-P05 | ✅ Hoàn thành; report [R01](reports/R01_retrieval-generation.md) |
| [H02 evaluation](handoffs/H02_evaluation.md) | 🟠 | H01 helper | ✅ Hoàn thành; report [R02](reports/R02_evaluation.md) |
| [H03 hoàn thiện](handoffs/H03_completion.md) | 🟠/🟢 | H01, H02 | ✅ Hoàn thành; report [R03](reports/R03_completion.md) |
| [H04 thẩm định](handoffs/H04_audit.md) | 🔴 | H03 | ✅ Hoàn thành; report [R04](reports/R04_audit.md) |

Checklist có hiệu lực:
- [x] Boot exit 0; đọc não/đề/review, chuẩn bị SPEC/handoffs.
- [x] Baseline 42 pass/0 fail/0 skip: evidence/handoff/baseline.txt; loader=8: evidence/handoff/loader.txt.
- [x] H01 core/parser/PageIndex và H02 evaluation hoàn tất, nộp report.
- [x] H03 corpus 8 verified/golden mới/index/A-B framework/UI hoàn tất, nộp report.
- [x] Live embedding/Generator: Jina và Gemini keys được nạp, index 560 chunks, benchmark hoàn tất 16/16 cases (run_20260926_032209_492532).
- [x] H04 thẩm định độc lập hoàn tất; nộp report R04 (phán quyết DUYỆT).

| Gate | local offline | local live |
| :-- | :-- | :-- |
| Test baseline | ✅ 42 pass | ✅ 42 pass (pytest.txt) |
| Corpus | ✅ loader=8 | ✅ 560 chunks indexed ChromaDB (idempotency.txt) |
| Provider/PageIndex | ✅ contract pass | ✅ Jina embeddings + Gemini LLM live smoke ok |
| Golden/A-B/calibration/UI | ✅ 16 grounded cases | ✅ complete: Config B 0.4732 vs Config A 0.4200 |

