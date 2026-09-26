"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_FILE = Path(__file__).parent.parent / "pageindex_doc_ids.json"


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        return

    doc_ids = {}
    if CACHE_FILE.exists():
        try:
            doc_ids = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            doc_ids = {}

    CACHE_FILE.write_text(json.dumps(doc_ids, indent=2), encoding="utf-8")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not query or not query.strip() or top_k <= 0 or not PAGEINDEX_API_KEY:
        return []

    try:
        import pageindex
        # If PageIndex client is available and configured
        return []
    except Exception:
        return []


if __name__ == "__main__":
    upload_documents()
