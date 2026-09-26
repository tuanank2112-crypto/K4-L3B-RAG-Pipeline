"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

import os
import hashlib
import json
import math
from functools import lru_cache
from urllib.parse import urlparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", str(Path(__file__).parent.parent / "chroma_db")))

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIM = 1536 if "text-embedding-3-small" in EMBEDDING_MODEL else 1024

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag_documents")


@lru_cache(maxsize=2)
def _local_model(model_name):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name)


def validate_vectors(vectors, count):
    if len(vectors) != count or not vectors:
        raise ValueError("Embedding vector count mismatch")
    dimension = len(vectors[0])
    if not dimension or any(len(v) != dimension or not all(math.isfinite(float(x)) for x in v) for v in vectors):
        raise ValueError("Embedding dimensions/finiteness invalid")
    return [[float(x) for x in vector] for vector in vectors]


def corpus_fingerprint(chunks=None):
    if chunks is None:
        chunks = chunk_documents(load_documents())
    payload = [{"id": c["id"], "content": c["content"], "metadata": c["metadata"]} for c in chunks]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Tạo embedding vectors cho danh sách texts theo provider được cấu hình."""
    if not texts:
        return []
    provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
    model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    if provider == "openai":
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        openai_client = OpenAI(api_key=api_key, base_url=base_url if base_url else None, timeout=60, max_retries=1)
        response = openai_client.embeddings.create(input=texts, model=model_name)
        return validate_vectors([item.embedding for item in sorted(response.data, key=lambda item: item.index)], len(texts))
    elif provider == "jina":
        import requests
        api_key = os.getenv("JINA_API_KEY")
        if not api_key:
            raise ValueError("JINA_API_KEY is missing in .env")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        data = {
            "model": os.getenv("EMBEDDING_MODEL", "jina-embeddings-v3"),
            "input": texts,
        }
        res = requests.post("https://api.jina.ai/v1/embeddings", headers=headers, json=data, timeout=30)
        res.raise_for_status()
        return validate_vectors([item["embedding"] for item in sorted(res.json()["data"], key=lambda item: item["index"])], len(texts))
    elif provider == "gemini":
        from google import genai
        from typing import Any
        gemini_client: Any = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        result = gemini_client.models.embed_content(model=model_name, contents=texts)
        return validate_vectors([item.values for item in (result.embeddings or [])], len(texts))
    elif provider == "sentence_transformers":
        return validate_vectors(_local_model(model_name).encode(texts, batch_size=32).tolist(), len(texts))
    else:
        raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {provider}")


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    import chromadb
    directory = Path(os.getenv("CHROMA_DIR", str(CHROMA_DIR)))
    directory.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(directory))
    expected = {"embedding_provider": os.getenv("EMBEDDING_PROVIDER", "openai"),
                "embedding_model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
                "corpus_sha256": corpus_fingerprint()}
    collection = client.get_or_create_collection(
        name=os.getenv("COLLECTION_NAME", COLLECTION_NAME),
        metadata={"hnsw:space": "cosine", **expected},
    )
    if collection.count() and any((collection.metadata or {}).get(k) != v for k, v in expected.items()):
        raise ValueError("Collection model/corpus mismatch; rebuild into a new COLLECTION_NAME (old data preserved)")
    return collection



def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    documents: list[dict] = []
    if not STANDARDIZED_DIR.exists():
        return documents
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        doc_type = "legal" if "legal" in path.parts else "news"
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        lines = content.splitlines()
        if any(line.strip() == "---" for line in lines):
            header_lines = []
            for line in lines:
                if line.strip() == "---":
                    break
                header_lines.append(line)
        else:
            header_lines = []
            for line in lines:
                if not line.strip():
                    break
                header_lines.append(line)

        fields = {}
        for line in header_lines:
            line_str = line.strip()
            if line_str.startswith("**") and ":**" in line_str:
                key, value = line_str[2:].split(":**", 1)
                fields[key.lower().strip()] = value.strip()
        if fields.get("verified", "").lower() != "true":
            continue
        source = fields.get("file") or path.name
        title = next((line[2:].strip() for line in header_lines if line.startswith("# ")), path.stem)
        candidate = fields.get("source", "")
        parsed = urlparse(candidate)
        url = candidate if parsed.scheme in ("http", "https") and parsed.netloc else None

        documents.append({
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": content,
            "metadata": {
                "source": source,
                "title": title,
                "doc_type": doc_type,
                "url": url,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        split_texts = splitter.split_text(document["content"])
        if not split_texts and document["content"]:
            split_texts = [document["content"]]
        for index, text in enumerate(split_texts):
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": {**document["metadata"], "chunk_index": index},
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return []
    texts = [chunk["content"] for chunk in chunks]
    vectors = validate_vectors(embed_texts(texts), len(chunks))
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return
    vectors = validate_vectors([chunk["embedding"] for chunk in chunks], len(chunks))
    if len({c["id"] for c in chunks}) != len(chunks):
        raise ValueError("Duplicate chunk IDs")
    collection = get_collection()
    metadata = dict(collection.metadata or {})
    if collection.count() and metadata.get("embedding_dimension") != len(vectors[0]):
        raise ValueError("Collection embedding dimension mismatch; use a new COLLECTION_NAME")
    fingerprint = corpus_fingerprint(chunks)
    if metadata.get("corpus_sha256") != fingerprint:
        raise ValueError("Input chunks do not match verified corpus; rebuild in a new collection")
    modify_metadata = {k: v for k, v in metadata.items() if k != "hnsw:space"}
    modify_metadata["embedding_dimension"] = len(vectors[0])
    collection.modify(metadata=modify_metadata)
    for offset in range(0, len(chunks), 128):
        batch = chunks[offset:offset + 128]
        metas = [{**c["metadata"], "url": c["metadata"].get("url") or ""} for c in batch]
        collection.upsert(ids=[c["id"] for c in batch], documents=[c["content"] for c in batch],
                          embeddings=vectors[offset:offset + 128], metadatas=metas)



def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks")


if __name__ == "__main__":
    run_pipeline()
