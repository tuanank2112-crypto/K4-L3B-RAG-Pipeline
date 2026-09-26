import os
import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="VinUni Student Services RAG Assistant",
    page_icon="🎓",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("🎓 VinUni RAG Assistant")
    st.markdown("**Hệ thống Hỏi đáp Quy chế & Dịch vụ Sinh viên**")
    st.divider()

    st.subheader("⚙️ Cấu hình truy xuất")
    top_k = st.slider("Số lượng đoạn trích (top_k)", min_value=3, max_value=10, value=5, step=1)
    
    st.divider()
    st.markdown("### 📚 Tài liệu trong hệ thống:")
    st.markdown("- **Quy chế đào tạo:** Academic Regulations (2024-10-30)")
    st.markdown("- **Hướng dẫn đánh giá:** Assessment Guidelines CHS (2024-06-12)")
    st.markdown("- **Sổ tay sinh viên:** VinUni Undergraduate Student Handbook (2020)")
    st.markdown("- **Dịch vụ & Thư viện:** Học liệu, Mượn trả & Thiết bị, Hỏi đáp Thủ thư, Cổng thông tin VinUni")
    
    st.divider()
    if st.button("🗑️ Xóa lịch sử trò chuyện"):
        st.session_state.messages = []
        st.rerun()

st.title("🎓 Trợ lý Tư vấn Quy chế & Dịch vụ Sinh viên")
st.caption("Tra cứu quy chế đào tạo, hướng dẫn đánh giá và dịch vụ sinh viên VinUni có dẫn nguồn trích dẫn minh bạch.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander(f"📌 Nguồn tham khảo ({len(message['sources'])} đoạn trích | Nguồn: {message.get('retrieval_source', 'unknown')})"):
                for idx, src in enumerate(message["sources"], 1):
                    meta = src.get("metadata", {})
                    title = meta.get("title", "Tài liệu")
                    source_name = meta.get("source", "N/A")
                    url = meta.get("url")
                    score = src.get("score", 0.0)
                    method = src.get("retrieval_method", "N/A")

                    st.markdown(f"**[{idx}] {title}** (`{src.get('id')}`)")
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        if url:
                            st.markdown(f"🔗 [Xem liên kết gốc]({url})")
                        else:
                            st.caption(f"Tệp: `{source_name}`")
                    with col2:
                        st.caption(f"Phương thức: `{method}`")
                    with col3:
                        st.caption(f"Score: `{score:.4f}`")

                    st.text(src.get("content", "").strip())
                    st.divider()

query = st.chat_input("Nhập câu hỏi của bạn (ví dụ: Sinh viên đại học được mượn tối đa bao nhiêu sách trong bao lâu?)...")

if query:
    query_text = query.strip()
    if not query_text:
        st.warning("Vui lòng nhập nội dung câu hỏi.")
    else:
        st.session_state.messages.append({"role": "user", "content": query_text})

        with st.chat_message("user"):
            st.markdown(query_text)

        with st.chat_message("assistant"):
            with st.spinner("Đang tìm kiếm thông tin và tổng hợp câu trả lời..."):
                try:
                    result = generate_with_citation(query_text, top_k=top_k)
                    answer = result.get("answer", "Không có câu trả lời.")
                    sources = result.get("sources", [])
                    retrieval_source = result.get("retrieval_source", "none")
                except Exception as error:
                    answer = "Hệ thống tạm thời không thể xử lý yêu cầu lúc này. Vui lòng thử lại sau."
                    sources = []
                    retrieval_source = "none"

                st.markdown(answer)

                if sources:
                    with st.expander(f"📌 Nguồn tham khảo ({len(sources)} đoạn trích | Nguồn: {retrieval_source})"):
                        for idx, src in enumerate(sources, 1):
                            meta = src.get("metadata", {})
                            title = meta.get("title", "Tài liệu")
                            source_name = meta.get("source", "N/A")
                            url = meta.get("url")
                            score = src.get("score", 0.0)
                            method = src.get("retrieval_method", "N/A")

                            st.markdown(f"**[{idx}] {title}** (`{src.get('id')}`)")
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                if url:
                                    st.markdown(f"🔗 [Xem liên kết gốc]({url})")
                                else:
                                    st.caption(f"Tệp: `{source_name}`")
                            with col2:
                                st.caption(f"Phương thức: `{method}`")
                            with col3:
                                st.caption(f"Score: `{score:.4f}`")

                            st.text(src.get("content", "").strip())
                            st.divider()

        # Save assistant message to session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "retrieval_source": retrieval_source,
        })
