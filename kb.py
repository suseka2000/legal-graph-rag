from parser import build_chunks_by_id, build_children_by_id
from retrieval import normalize, build_dense_index
from loaders import load_document, parse_document

from pathlib import Path
from rank_bm25 import BM25Okapi


class KnowledgeBase:

    def __init__(
        self,
        documents_path: str
    ):

        self.documents_path = documents_path

        print(
            "Loading documents..."
        )

        self.chunks = (
            self._load_chunks()
        )

        print(
            f"Loaded {len(self.chunks)} chunks"
        )

        self.chunks_by_id = (
            build_chunks_by_id(
                self.chunks
            )
        )

        self.children_by_id = (
            build_children_by_id(
                self.chunks
            )
        )

        print(
            "Building BM25 index..."
        )

        tokenized_chunks = [
            normalize(
                f"{c.section}\n{c.text}"
            )
            for c in self.chunks
        ]

        self.bm25 = BM25Okapi(
            tokenized_chunks
        )

        print(
            "Building dense index..."
        )

        self.dense_index = (
            build_dense_index(
                self.chunks
            )
        )

        print(
            "Knowledge base ready."
        )

    def _load_chunks(self):

        all_chunks = []

        for path in Path(
            self.documents_path
        ).rglob("*"):

            if (
                path.suffix.lower()
                not in {
                    ".pdf",
                    ".docx",
                    ".txt"
                }
            ):
                continue

            try:

                print(
                    f"Parsing {path.name}"
                )

                text = load_document(
                    str(path)
                )

                chunks = (
                    parse_document(
                        doc_name=path.name,
                        text=text
                    )
                )

                all_chunks.extend(
                    chunks
                )

            except Exception as e:

                print(
                    f"Failed {path}: {e}"
                )

        return all_chunks