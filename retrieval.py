import re
import pymorphy3
from rank_bm25 import BM25Okapi

morph = pymorphy3.MorphAnalyzer()

def normalize(text):

    words = re.findall(
        r"\w+",
        text.lower()
    )

    return [
        morph.parse(word)[0].normal_form
        for word in words
    ]

def sparse_search(query, bm25, chunks, k):

    tokens = normalize(query)

    scores = bm25.get_scores(tokens)

    ranked = sorted(
        enumerate(scores),
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    for idx, score in ranked[:k]:

        results.append({
            "score": float(score),
            "chunk": chunks[idx]
        })

    return results

from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("intfloat/multilingual-e5-small")

def embed_query(text: str):
    return model.encode(
        f"query: {text}",
        normalize_embeddings=True
    )


def embed_doc(text: str):
    return model.encode(
        f"passage: {text}",
        normalize_embeddings=True
    )

def build_dense_index(chunks):

    texts = [
        f"passage: {c.section}\n{c.text}"
        for c in chunks
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=True
    )

    return np.array(embeddings)

def dense_search(query, chunks, dense_index, k=5):

    chunk_embeddings = dense_index

    q = embed_query(query)

    scores = np.dot(chunk_embeddings, q)

    top_idx = np.argsort(scores)[::-1][:k]

    return [
        {
            "score": float(scores[i]),
            "chunk": chunks[i]
        }
        for i in top_idx
    ]

def rrf(rank, k=60):
    return 1.0 / (k + rank)

def hybrid_search(
    query,
    bm25,
    chunks,
    dense_index,
    top_k
):

    sparse = sparse_search(
        query = query,
        bm25=bm25,
        chunks=chunks,
        k=top_k
    )

    dense = dense_search(
        query=query,
        chunks=chunks,
        dense_index=dense_index,
        k=top_k
    )

    scores = {}

    for rank, item in enumerate(
        sparse,
        start=1
    ):

        cid = item["chunk"].id

        scores[cid] = (
            scores.get(cid, 0)
            + rrf(rank)
        )

    for rank, item in enumerate(
        dense,
        start=1
    ):

        cid = item["chunk"].id

        scores[cid] = (
            scores.get(cid, 0)
            + rrf(rank)
        )

    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    for cid, score in ranked[:top_k]:

        results.append({
            "chunk": chunks_by_id[cid],
            "score": score
        })

    return results