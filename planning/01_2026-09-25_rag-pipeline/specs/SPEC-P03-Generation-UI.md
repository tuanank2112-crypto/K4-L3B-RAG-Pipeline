# P03 — Generation và UI
## Contract
Task 10 và app.py dùng [GenerationResult](01-CONTRACTS.md).
reorder_for_llm trả list mới, bảo toàn ID, chunk tốt nhất ở đầu. format_context có title/source và nhãn chunk ID ổn định.
Answer dùng nhãn [chunk-id]; kiểm mọi nhãn có trong sources. sources giữ thứ tự score giảm dần dù context reorder.
call_llm dispatch theo LLM_PROVIDER/LLM_MODEL; trả text; lazy-init SDK khi cần.
generate_with_citation trả refusal {answer: thông báo thiếu bằng chứng, sources: [], retrieval_source: none} khi không thể tạo câu trả lời có căn cứ.
UI gọi hàm này và lưu answer/sources trong session_state; hiển thị source/title/url, method và score.

## Bắt buộc / vùng cấm
BẮT BUỘC coi nội dung tài liệu là dữ liệu, không phải chỉ thị; prompt yêu cầu chỉ trả lời từ context.
CẤM bịa citation hoặc coi tồn tại nhãn citation là bằng chứng nội dung đúng.
CẤM nuốt lỗi key bằng một câu trả lời có vẻ thành công; UI cần thông báo thân thiện.
Không thêm memory đa lượt hoặc deployment trước core; giữ UI Streamlit hiện tại.

## Lỗi và caller
| Lỗi | Hành vi |
| :-- | :-- |
| Thiếu key/model hoặc provider lỗi | Safe refusal, UI vẫn hoạt động; log không key |
| Không có context | Refusal, không gọi LLM |
| Citation ngoài sources hoặc trả lời không có citation | Không công bố đáp án chưa xác minh; refusal |
| Người dùng gửi query trắng | Bỏ qua/gợi ý nhập câu hỏi |

## Nghiệm thu
python -m pytest tests/test_contracts.py -q -k "reorder or generation" → exit 0.
Bổ sung mock tests cho dispatch 3 provider, citation sau reorder, provider error, context rỗng, citation lạ.
streamlit run app.py: demo câu hỏi có nguồn, ngoài domain, lỗi provider; mỗi lần UI không crash, nguồn bấm được khi có URL.
Lưu kết quả smoke ở evidence/P03/*.txt; chưa gọi provider thật trong planning.
