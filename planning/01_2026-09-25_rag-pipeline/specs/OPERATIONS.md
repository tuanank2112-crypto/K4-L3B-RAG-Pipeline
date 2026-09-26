# Vận hành local
## Contract thao tác
Chạy từ root K4-L3B-RAG-Pipeline. Engine:
```powershell
node ../../../brain4agent.release/.agents/skills/.xay-dung-nao-bo/scripts/init_brain.js --check
```
0=đạt, 1=cần engine ghi một lần rồi check lại, 2=cần xử lý điều kiện được báo, 5=provenance; không tự sửa luật.
Python >=3.10,<3.14; hiện máy có Python 3.13.15. Chưa xác minh cài đầy đủ dependencies.
```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"
.venv/Scripts/python.exe -m playwright install chromium
```
Chỉ copy .env.example thành .env nếu chưa tồn tại; cấu hình provider/model và key ngoài Git.
Thứ tự: collect/crawl → convert → index → contract tests → Streamlit → evaluation → acceptance.
Nếu không activate venv, dùng .venv/Scripts/python.exe cho mọi lệnh Python và python -m streamlit run app.py.

## Bắt buộc / vùng cấm
BẮT BUỘC thêm chroma_db/ vào ignore khi bắt đầu sinh index; hiện .gitignore chưa có.
BẮT BUỘC snapshot/config fingerprint trước rebuild model; không ghi đè .env có sẵn.
Không push, deploy, xóa DB hoặc reset thay đổi của người dùng trong kế hoạch local.

## Rollback và lỗi
| Lỗi | Hành vi caller |
| :-- | :-- |
| Dependency không tương thích | Ghi pip log; điều chỉnh môi trường có kiểm soát, không đổi contract |
| Index hỏng/sai dimension | Giữ bản cũ, tạo index mới từ corpus snapshot; chuyển cấu hình sau kiểm tra |
| Thi công lỗi | Hoàn tác đúng file/commit của gói; bảo toàn corpus và thay đổi người dùng |
| Brain engine provenance lỗi | Dừng sửa hub; báo lỗi và path thật |

## Nghiệm thu
Boot check exit 0; chạy mới trong venv tái lập được; không tracked .env/key/cache.
Lưu lệnh, exit code và output vào evidence/<gói>/*.txt, không ghi key.
Không dùng npm run gate: repo Python này không có script đó.
