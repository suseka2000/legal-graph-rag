chunks = parse_directory(
    "./documents"
)

chunks_by_id = build_chunks_by_id(
    chunks
)

children_by_id = build_children_by_id(
    chunks
)

dense_index = build_dense_index(
    chunks
)

tokenized_chunks = [
    normalize(
        c.section + "\n" + c.text
    )
    for c in chunks
]

bm25 = BM25Okapi(
    tokenized_chunks
)

def retrieve(query: str, top_k: int = 5):

    results = hybrid_search(
        query=query,
        bm25=bm25,
        chunks=chunks,
        dense_index=dense_index,
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

def read_chunk(chunk_id: str):

    chunk = chunks_by_id.get(chunk_id)

    if chunk is None:
        return {
            "error": "chunk not found"
        }

    return {
        "chunk_id": chunk.id,
        "section": chunk.section,
        "text": chunk.text
    }

def expand_path(chunk_id: str):

    chunk = chunks_by_id.get(chunk_id)

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

        current = chunks_by_id.get(
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
    chunk_id: str,
    window: int = 1
):

    chunk = chunks_by_id.get(chunk_id)

    if chunk is None:
        return []

    parent_id = chunk.parent_id

    if parent_id is None:
        return []

    siblings = children_by_id.get(
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

        c = chunks_by_id[cid]

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

import json

def execute_tool(tool_call):

    name = tool_call.function.name

    arguments = json.loads(
        tool_call.function.arguments
    )

    tool = TOOLS[name]

    return tool(**arguments)

SYSTEM_PROMPT = """
Ты агент по нормативным документам.

Для ответа используй инструменты.

Алгоритм:
1. Сначала вызови retrieve().
2. Затем expand_path().
3. Затем read_chunk().
4. При необходимости вызови get_neighbors().
5. После получения достаточной информации дай ответ.

ВАЖНО:
Всегда отвечай ТОЛЬКО на русском языке.
Никогда не используй китайский, английский или другие языки.
Все ответы, рассуждения и объяснения должны быть исключительно на русском языке.
Если цитируешь документ, сохраняй язык оригинала документа.

Никогда не придумывай факты.
Всегда опирайся на результаты инструментов.
"""

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

def run_agent(
    client,
    kb,
    t : float,
    question: str,
    max_steps: int = 10
):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": question
        }
    ]

    for _ in range(max_steps):

        response = client.chat.completions.create(
            model="qwen2.5:7b",
            messages=messages,
            tools=tool_schemas,
            temperature = t
        )

        msg = response.choices[0].message

        if not msg.tool_calls:

            return msg.content

        messages.append(msg)

        for tc in msg.tool_calls:

            result = execute_tool(tc)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(
                        result,
                        ensure_ascii=False
                    )
                }
            )

    return msg.content