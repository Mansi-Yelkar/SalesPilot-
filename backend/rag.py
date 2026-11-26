"""
rag.py — Retrieval-Augmented Generation using Sentence Transformers + FAISS.
Loads company_knowledge.txt, chunks it, and builds a semantic search index.
"""

import os
import re
from typing import List

KNOWLEDGE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "company_knowledge.txt"
)
CHUNK_SIZE = 200  # approximate words per chunk


def _load_and_chunk(path: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """Split the knowledge document into overlapping word-based chunks."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Normalise whitespace
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()
    chunks = []
    step = chunk_size - 20  # 20-word overlap
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


class RAGEngine:
    def __init__(self) -> None:
        self._chunks: List[str] = []
        self._index = None
        self._model = None
        self._ready = False

    def build(self) -> None:
        """Load document, create embeddings, and build FAISS index."""
        try:
            import numpy as np
            from sentence_transformers import SentenceTransformer
            import faiss  # type: ignore

            self._chunks = _load_and_chunk(KNOWLEDGE_PATH)
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = self._model.encode(
                self._chunks, show_progress_bar=False, normalize_embeddings=True
            )
            embeddings = np.array(embeddings, dtype="float32")
            dim = embeddings.shape[1]
            self._index = faiss.IndexFlatIP(dim)  # inner-product == cosine for normalised vecs
            self._index.add(embeddings)
            self._ready = True
            print(
                f"[RAG] Index built with {len(self._chunks)} chunks "
                f"from '{KNOWLEDGE_PATH}'."
            )
        except Exception as exc:
            print(f"[RAG] Warning: could not build index — {exc}")
            self._ready = False

    def retrieve(self, query: str, k: int = 3) -> str:
        """Return top-k relevant passages as a single string, or '' if unavailable."""
        if not self._ready or not self._chunks:
            return ""
        try:
            q_emb = self._model.encode(
                [query], normalize_embeddings=True
            ).astype("float32")
            _, indices = self._index.search(q_emb, min(k, len(self._chunks)))
            passages = [self._chunks[i] for i in indices[0] if i >= 0]
            return "\n---\n".join(passages)
        except Exception as exc:
            print(f"[RAG] Retrieval error: {exc}")
            return ""


# Singleton instance initialised when the module is first imported
rag_engine = RAGEngine()
