# P05 — Hợp đồng tiếp tục và nghiệm thu lab

## 1. Đầu vào và thứ tự
Áp dụng cùng 00-ARCHITECTURE, 01-CONTRACTS, P01–P04, OPERATIONS và TESTING-ACCEPTANCE; không thay contract đề lab.
Thứ tự worker: H01 (tiếp tục core) → H02 (rà evaluation sau helper) → H03 (corpus/golden/live/report) → H04 (thẩm định cô lập).
H01/H02 trước đã dừng do quota, code dang dở được giữ; không coi là hoàn tất. `evidence/handoff/baseline.txt`: 42 pass, 0 fail, 0 skip, exit 0. Tuy nhiên `load_documents()` đang trả 0 vì chỉ đọc header trước dòng trắng đầu tiên; PageIndex vẫn stub. Test xanh chưa chứng minh sản phẩm chạy.

## 2. Corpus và provenance
`data/landing/legal/manifest.json`: list `{filename,title,url,resolved_url,date_crawled,sha256,bytes,verified}`. SHA256 khớp bytes PDF; verified=true chỉ khi tải HTTP thành công và kiểm PDF.
Ba PDF mới: academic_regulations.pdf (2024-10-30), assessment_guidelines.pdf (2024-06-12), student_handbook.pdf (2020, lịch sử).
News `article_01..05.json`: giữ schema đề, thêm verified, response_sha256, content_sha256, resolved_url. Năm URL có trong task2. Giữ các ô bảng thành hàng phân cách ` | `; loại navigation/header/footer.
Markdown header: `# <title>`, `**Source:** <HTTP(S) URL>`, `**File:** <filename>`, `**Verified:** true`, `**Crawled:** <ISO8601>`, rồi dòng `---`; các field cách nhau dòng trắng.
BẮT BUỘC loader đọc toàn bộ header trước delimiter, trả đúng 8 tài liệu verified (3 legal + 5 news); source=filename, title=tên thật, url hợp lệ. CẤM index ba Markdown/PDF giả cũ; giữ nguyên chúng, không xóa không hỏi.
Handbook 2020 chỉ trả lời câu có mốc lịch sử hoặc điều không mâu thuẫn; khi khác quy định 2024 dùng nguồn mới hơn. CẤM tự nhận snapshot là quy định hiện hành chưa xác minh.

## 3. Golden và evaluation
Golden ≥15 row `{question,expected_answer,expected_context,source_ids:list[str]}`. source_ids là Document.id của load_documents. expected_context là đoạn nguồn thật, exact sau normalize whitespace; đáp án người soạn đọc đối chiếu, không lấy LLM làm ground truth.
BẮT BUỘC thay golden cũ dựa corpus giả; bao phủ policy và dịch vụ, ghi edition trong câu khi cần. Calibration riêng ≥5 in-domain + ≥5 out-domain, không trùng golden.
Runner giữ `python -m src.evaluate --config both`, top_k=5 mặc định. A dense-only/B hybrid+RRF, fallback tắt, cùng generator/prompt/model/corpus. Raw ghi fingerprints và từng case; case lỗi metrics=null, run incomplete exit nonzero, không kết luận A/B.
4 metric hiện là token-overlap heuristic: phải công bố công thức/hạn chế, không gọi là RAGAS/độ đúng semantic. Không bịa bonus/cost/delta. RESULT và báo cáo cá nhân lấy raw thật, không tự xác nhận đóng góp của học viên.

## 4. Provider, index và UI
Bộ nhớ phiên trước yêu cầu API, không tải model nặng local. Giữ yêu cầu này: JINA_API_KEY/PAGEINDEX_API_KEY hiện trống; key generation có nhưng chưa smoke. CẤM mua credit hoặc thay provider âm thầm. Có thể kiểm endpoint/model embedding trên tài khoản đã cấu hình; thiếu quyền thì ghi blocked cụ thể.
Đợt pip cài sentence-transformers/pageindex đã dừng; chỉ beautifulsoup4 được xác nhận cài. Không coi import spec là dependency đầy đủ.
Giữ .env và DB cũ; index thật trong collection/path mới qua env, ghi config. Chạy upsert hai lần cùng chunks, count bằng unique IDs; dense/BM25 tiến trình mới dùng cùng IDs. SCORE_THRESHOLD phải dùng cosine gốc và có calibration evidence; không so RRF.
`generate_from_chunks(query: str,chunks: list[dict]) -> GenerationResult`: shared helper; provider lỗi/invalid citation raise để benchmark ghi error; `generate_with_citation` safe-wrap trả refusal. Sửa ký tự tiếng Việt hỏng trong prompt; nguồn không phải chỉ thị.
PageIndex: adapter theo docs/SDK chính thức hiện hành, upload có hash/id mapping và timeout; kết quả SearchResult từ văn bản nguồn, không dùng câu trả lời LLM của dịch vụ làm bằng chứng gốc. Thiếu key không crash; mock không thay live gate.
UI đổi danh mục/chào/ví dụ phù hợp corpus thật, bỏ số liệu học bổng/KTX cũ. Hiển thị edition, ID citation, nguồn HTTP(S), score/method. Không đưa exception có secrets lên UI.

## 5. Phân loại lỗi và caller
| Lỗi | Hành vi bắt buộc |
| :-- | :-- |
| Header đọc sai / hash sai / corpus rỗng | Dừng trước embedding; sửa parser/provenance, test đỏ rồi xanh |
| API thiếu key/quota/timeout | Không đổi thành điểm 0 hoặc sparse-only A/B; ghi thiếu cấu hình, giữ gate mở |
| PageIndex chưa ready / mapping sai | Retry hữu hạn hoặc hybrid/refusal; không tự bịa nguồn |
| Index model/corpus khác | Fail rõ, bảo toàn DB cũ, dùng namespace mới |
| Golden không grounded / dữ liệu cũ | Runner exit nonzero trước API |
| Worker quota / ngắt phiên | Lưu report partial đúng phạm vi; người sau tiếp tục, không đánh dấu đạt |

## 6. Đo và exit gates
`python -m pytest -q -p no:cacheprovider`: ≥42 test, 0 fail/skip, giữ 20 test gốc. Bổ sung ca parse header thực tế, provenance tamper, PageIndex thành công/lỗi/timeout, citation, A-only/B-only/provider error, dense/BM25 cùng corpus.
`python -m compileall -q src app.py` exit 0; `python -m ruff check src tests app.py --select E9,F63,F7,F82` exit 0; `python -m mypy src --ignore-missing-imports --follow-imports=silent` exit 0. Không blanket-ignore lỗi mới để đạt.
Lưu output máy và exit code vào evidence/P01..P05; corpus-count: 8/3/5; idempotency duplicate=0; calibration có 10 query+score+threshold; A/B ≥15 cases mỗi cấu hình complete. Demo UI: có nguồn, ngoài domain, provider lỗi.
H04 đo lại độc lập và thử ≥3 cách phá, không đọc report/handoff worker. Không sửa working tree để tạo mutant: dùng tmp_path hoặc bản sao tạm ngoài root.
Thiếu live key => gate ⬜, không đóng kế hoạch. Worker báo hết việc/chờ review; chỉ người duyệt đóng hồ sơ sau mọi H có R và evidence tồn tại. Version giữ 0.1.0 lúc planning; chỉ bump 0.1.1 khi patch được nghiệm thu, không trộn brain_template_version.
