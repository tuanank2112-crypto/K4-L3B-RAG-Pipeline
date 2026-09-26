"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

import math

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if not query or not query.strip() or top_k <= 0:
        return []

    query_vectors = embed_texts([query])
    if not query_vectors:
        return []
    query_vector = query_vectors[0]

    collection = get_collection()
    response = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    ids = response.get("ids", [[]])[0]
    docs = response.get("documents", [[]])[0]
    metas = response.get("metadatas", [[]])[0]
    dists = response.get("distances", [[]])[0]

    results_by_id: dict[str, dict] = {}
    for item_id, content, raw_meta, distance in zip(ids, docs, metas, dists):
        if not math.isfinite(float(distance)):
            continue
        score = 1.0 - float(distance)
        meta = dict(raw_meta) if raw_meta else {}
        if not meta.get("url"):
            meta["url"] = None
        if "chunk_index" in meta:
            meta["chunk_index"] = int(meta["chunk_index"])

        if item_id in results_by_id:
            if score > float(results_by_id[item_id]["score"]):
                results_by_id[item_id]["score"] = score
        else:
            results_by_id[item_id] = {
                "id": str(item_id),
                "content": str(content),
                "score": score,
                "metadata": meta,
                "retrieval_method": "dense",
            }

    sorted_results = sorted(
        results_by_id.values(),
        key=lambda item: (-float(item["score"]), str(item["id"])),
    )
    return sorted_results[:top_k]


if __name__ == "__main__":
    for result in semantic_search("test query", top_k=3):
        print(result)
