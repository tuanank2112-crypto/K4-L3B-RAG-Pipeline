"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os
import re
import time
import logging
from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Bạn là trợ lý AI trả lời câu hỏi dựa trên các tài liệu được cung cấp.
Quy tắc:
1. Trả lời CHỈ từ context được cung cấp. Không tự ý suy diễn hoặc bịa đặt.
2. Trích dẫn nguồn chính xác bằng ID tài liệu trong ngoặc vuông, ví dụ [tên_file::chunk-0].
3. Nếu thông tin không đủ trong context, hãy từ chối trả lời một cách lịch sự: "Tôi không thể xác minh thông tin này từ nguồn hiện có."
"""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context (giảm lost-in-the-middle)."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label rõ ràng cho từng chunk."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Untitled")
        source = metadata.get("source", "Unknown")
        chunk_id = chunk.get("id", f"chunk-{index}")
        parts.append(
            f"[{chunk_id} | Title: {title} | Source: {source}]\n{chunk.get('content', '')}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model = os.getenv("LLM_MODEL", "").strip()

    if provider == "openai":
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        openai_client = OpenAI(api_key=api_key, base_url=base_url if base_url else None, timeout=60, max_retries=1)
        target_model = model or "gpt-4o-mini"
        response = openai_client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
            max_tokens=1000,
        )
        return str(response.choices[0].message.content or "")

    elif provider == "gemini":
        from google import genai
        from typing import Any
        api_key = os.getenv("GEMINI_API_KEY")
        gemini_client: Any = genai.Client(api_key=api_key, http_options={"timeout": 60000})
        target_model = model or "gemini-3.5-flash-lite"
        full_prompt = f"{system_prompt}\n\n---\n\n{user_message}"
        for attempt in range(3):
            try:
                response = gemini_client.models.generate_content(
                    model=target_model,
                    contents=full_prompt,
                )
                return str(response.text or "")
            except Exception as e:
                err_str = str(e).lower()
                if attempt < 2 and any(k in err_str for k in ["504", "503", "429", "deadline", "unavailable", "timeout", "resource_exhausted"]):
                    time.sleep(2 * (attempt + 1))
                    continue
                raise
        return ""

    elif provider == "anthropic":
        from anthropic import Anthropic
        from typing import Any
        api_key = os.getenv("ANTHROPIC_API_KEY")
        anthropic_client: Any = Anthropic(api_key=api_key, timeout=60, max_retries=1)
        target_model = model or "claude-3-5-haiku-latest"
        response = anthropic_client.messages.create(
            model=target_model,
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=TEMPERATURE,
        )
        return str(response.content[0].text or "")

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


def is_greeting(query: str) -> bool:
    """Kiểm tra xem câu hỏi có phải là câu chào hỏi mở đầu không."""
    import re
    q = query.strip().lower()
    patterns = [
        r"^(xin\s+)?chào(\s+bạn|\s+ad|\s+bot)?[\s\!\?\.]*$",
        r"^(hello|hi|hey)[\s\!\?\.]*$",
        r"^(bạn\s+là\s+ai|bạn\s+giúp\s+được\s+gì|hướng\s+dẫn(\s+sử\s+dụng)?)[\s\!\?\.]*$",
    ]
    return any(re.match(p, q) for p in patterns)


GREETING_MESSAGE = "Xin chào! Tôi hỗ trợ tra cứu quy chế và thông tin sinh viên VinUni từ tài liệu có nguồn. Bạn hãy nhập câu hỏi cụ thể."
REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."


def _refusal():
    return {"answer": REFUSAL, "sources": [], "retrieval_source": "none"}


def generate_from_chunks(query: str, chunks: list[dict]) -> dict:
    """Shared generation path; provider failures propagate to benchmark callers."""
    if not query or not query.strip() or not chunks:
        return _refusal()
    sources = sorted(chunks, key=lambda c: (-c["score"], c["id"]))
    context = format_context(reorder_for_llm(sources))
    answer = call_llm(SYSTEM_PROMPT, f"Context:\n{context}\n\nCâu hỏi: {query}")
    raw_labels = re.findall(r"\[([^\[\]\n]+)\]", answer or "")
    labels = [part.strip() for item in raw_labels for p in item.split(";") for part in p.split(",") if part.strip()]
    ids = {c["id"] for c in sources}
    if answer and answer.strip() == REFUSAL:
        return _refusal()
    if not answer or not answer.strip() or not labels or any(label not in ids for label in labels):
        raise ValueError("Invalid generation citation or empty answer")
    return {"answer": answer.strip(), "sources": sources,
            "retrieval_source": "pageindex" if sources[0].get("retrieval_method") == "pageindex" else "hybrid"}


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Safe UI wrapper; never expose provider exception payloads."""
    if not query or not query.strip() or top_k <= 0:
        return _refusal()
    if is_greeting(query):
        return {"answer": GREETING_MESSAGE, "sources": [], "retrieval_source": "none"}
    try:
        return generate_from_chunks(query, retrieve(query, top_k=top_k))
    except Exception as error:
        logging.getLogger(__name__).warning("Generation unavailable (%s)", type(error).__name__)
        return _refusal()


if __name__ == "__main__":
    print(generate_with_citation("test query"))
