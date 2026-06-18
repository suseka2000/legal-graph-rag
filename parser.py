import re
from collections import defaultdict

PATTERNS = {
    "chapter": re.compile(r"^(Глава\s+\d+\.?.*)$", re.MULTILINE),
    "section": re.compile(r"^(Раздел\s+[IVXLCDM\d]+\.?.*)$", re.MULTILINE),
    "article": re.compile(r"^(Статья\s+\d+(\.\d+)?\.?.*)$", re.MULTILINE),
    "point": re.compile(r"^(\d+(\.\d+)*\.)\s", re.MULTILINE),
}

def extract_structured_headers(text: str):

    headers = []

    for level, pattern in PATTERNS.items():

        for m in pattern.finditer(text):

            headers.append({
                "level": level,
                "title": m.group(1).strip(),
                "start": m.start()
            })

    return sorted(headers, key=lambda x: x["start"])

LEVEL_ORDER = ["section", "chapter", "article", "point"]

def _update_stack(stack, header, node_id, level):

    # убираем всё что глубже или равно текущему уровню
    while stack:
        last_level = stack[-1]["level"]

        if LEVEL_ORDER.index(last_level) >= LEVEL_ORDER.index(level):
            stack.pop()
        else:
            break

    stack.append({
        "id": node_id,
        "level": level
    })

def expand_path(chunk, chunks_by_id):

    path = []
    seen_levels = set()

    current = chunk

    while current:

        # берём только 1 узел каждого уровня
        if current.level not in seen_levels:

            path.append(current)
            seen_levels.add(current.level)

        if not current.parent_id:
            break

        current = chunks_by_id.get(current.parent_id)

    return list(reversed(path))

def build_chunks_by_id(chunks):

    return {
        chunk.id: chunk
        for chunk in chunks
    }

def build_children_by_id(chunks):

    children = defaultdict(list)

    for chunk in chunks:

        if chunk.parent_id:

            children[
                chunk.parent_id
            ].append(chunk.id)

    return dict(children)