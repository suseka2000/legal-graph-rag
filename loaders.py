from pathlib import Path
import fitz  # pymupdf
from docx import Document
import os

def load_documents_from_dir(directory: str):
    paths = []

    for path in Path(directory).rglob("*"):

        if path.suffix.lower() in {
            ".pdf",
            ".docx",
            ".txt"
        }:
            paths.append(path)

    return paths

def load_pdf_as_text(path: str) -> str:
    doc = fitz.open(path)

    pages_text = []

    for page in doc:
        text = page.get_text("text")

        # нормализация
        text = text.replace("\r", "").strip()

        if text:
            pages_text.append(text)

    return "\n\n".join(pages_text)

def load_docx_as_text(path: str) -> str:
    doc = Document(path)

    paragraphs = []

    for p in doc.paragraphs:
        text = p.text.strip()

        if not text:
            continue

        paragraphs.append(text)

    return "\n\n".join(paragraphs)

def load_document(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        return load_pdf_as_text(path)

    if ext == ".docx":
        return load_docx_as_text(path)

    raise ValueError(f"Unsupported format: {ext}")

def parse_directory(directory: str):

    all_chunks = []

    paths = load_documents_from_dir(directory)

    for path in paths:

        print(f"Parsing {path}")

        try:

            text = load_document(str(path))

            chunks = parse_document(
                doc_name=path.name,
                text=text
            )

            all_chunks.extend(chunks)

        except Exception as e:

            print(
                f"Failed {path}: {e}"
            )

    return all_chunks

import uuid

def parse_document(doc_name: str, text: str):

    headers = extract_structured_headers(text)

    if not headers:
        return [
            Chunk(
                id=str(uuid.uuid4()),
                doc_name=doc_name,
                section="DOCUMENT",
                text=text
            )
        ]

    chunks = []
    stack = []  # хранит текущую иерархию

    for i, h in enumerate(headers):

        start = h["start"]
        end = headers[i + 1]["start"] if i + 1 < len(headers) else len(text)

        content = text[start:end].strip()

        node_id = str(uuid.uuid4())

        # определяем parent
        parent_id = stack[-1]["id"] if stack else None

        chunk = Chunk(
            id=node_id,
            doc_name=doc_name,
            level=h["level"],
            section=h["title"],
            text=content,
            parent_id=parent_id
        )

        chunks.append(chunk)

        # обновляем стек по уровню
        _update_stack(stack, h, node_id, h["level"])

    return chunks