from retrieval import hybrid_search
import json

def retrieve(kb, query: str, top_k: int = 5):

    results = hybrid_search(
        query=query,
        bm25=kb.bm25,
        chunks=kb.chunks,
        dense_index=kb.dense_index,
        chunks_by_id=kb.chunks_by_id,
        top_k=top_k
    )

    return [
        {
            "chunk_id": r["chunk"].id,
            "section": r["chunk"].section,
            "score": round(r["score"], 4)
        }
        for r in results
    ]

def read_chunk(kb, chunk_id: str):

    chunk = kb.chunks_by_id.get(chunk_id)

    if chunk is None:
        return {
            "error": "chunk not found"
        }

    return {
        "chunk_id": chunk.id,
        "section": chunk.section,
        "text": chunk.text
    }

def expand_path(kb, chunk_id: str):

    chunk = kb.chunks_by_id.get(chunk_id)

    if chunk is None:
        return []

    chapter = None
    article = None
    point = None

    current = chunk

    while current:

        if current.level == "chapter":
            chapter = current.section

        elif current.level == "article":
            article = current.section

        elif current.level == "point":
            point = current.section

        if not current.parent_id:
            break

        current = kb.chunks_by_id.get(
            current.parent_id
        )

    result = []

    if chapter:
        result.append(chapter)

    if article:
        result.append(article)

    if point:
        result.append(point)

    return result

def get_neighbors(
    kb,
    chunk_id: str,
    window: int = 1
):

    chunk = kb.chunks_by_id.get(chunk_id)

    if chunk is None:
        return []

    parent_id = chunk.parent_id

    if parent_id is None:
        return []

    siblings = kb.children_by_id.get(
        parent_id,
        []
    )

    try:
        idx = siblings.index(chunk_id)

    except ValueError:
        return []

    start = max(
        0,
        idx - window
    )

    end = min(
        len(siblings),
        idx + window + 1
    )

    result = []

    for cid in siblings[start:end]:

        c = kb.chunks_by_id[cid]

        result.append({
            "chunk_id": c.id,
            "section": c.section,
            "text": c.text
        })

    return result


TOOLS = {
    "retrieve": retrieve,
    "read_chunk": read_chunk,
    "expand_path": expand_path,
    "get_neighbors": get_neighbors,
}

tool_schemas = [
    {
        "type": "function",
        "function": {
            "name": "retrieve",
            "description": (
                "Search relevant chunks."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_chunk",
            "description": (
                "Read full chunk text."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "chunk_id": {
                        "type": "string"
                    }
                },
                "required": ["chunk_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "expand_path",
            "description": (
                "Get chapter/article/point path."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "chunk_id": {
                        "type": "string"
                    }
                },
                "required": ["chunk_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_neighbors",
            "description": (
                "Get neighboring chunks."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "chunk_id": {
                        "type": "string"
                    },
                    "window": {
                        "type": "integer"
                    }
                },
                "required": ["chunk_id"]
            }
        }
    }
]