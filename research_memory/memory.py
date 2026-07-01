"""
Research memory: a ChromaDB vector store of PAST user-research studies.

This is the RAG layer. Past study notes are split into chunks, embedded with
Gemini's embedding model, and stored in a local ChromaDB collection. The
`search_research_memory` function (used as an agent tool) finds the chunks most
relevant to a question, so the librarian agent can answer across many studies.
"""

import os
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from google import genai

# Gemini's embedding model. If this name ever errors, try "gemini-embedding-001".
EMBED_MODEL = ""gemini-embedding-001"

# Where the vector DB lives on disk (created automatically, git-ignored).
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "research_memory_db")
COLLECTION_NAME = "past_studies"


class GeminiEmbeddingFunction(EmbeddingFunction):
    """Turns text into vectors using Gemini, so ChromaDB can do similarity search.

    Reuses the same GOOGLE_API_KEY as the rest of the project, so there is no
    extra setup and no heavy local model download.
    """

    def __init__(self):
        self._client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    def __call__(self, input: Documents) -> Embeddings:
        resp = self._client.models.embed_content(
            model=EMBED_MODEL, contents=list(input)
        )
        return [list(e.values) for e in resp.embeddings]

    @staticmethod
    def name() -> str:
        return "gemini_embedding"

    def get_config(self):
        return {}

    @classmethod
    def build_from_config(cls, config):
        return cls()


def get_collection():
    """Open (or create) the on-disk ChromaDB collection of past studies."""
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=GeminiEmbeddingFunction()
    )


def _chunk(text: str, size: int = 700):
    """Split a study into ~paragraph-sized chunks for better retrieval."""
    parts, current = [], ""
    for para in text.split("\n\n"):
        if len(current) + len(para) > size and current:
            parts.append(current.strip())
            current = ""
        current += para + "\n\n"
    if current.strip():
        parts.append(current.strip())
    return parts


def add_study(study_name: str, text: str):
    """Add one study's notes to memory, split into chunks."""
    col = get_collection()
    chunks = _chunk(text)
    col.add(
        documents=chunks,
        metadatas=[{"study": study_name} for _ in chunks],
        ids=[f"{study_name}::{i}" for i in range(len(chunks))],
    )
    return len(chunks)


def search_research_memory(query: str) -> str:
    """Search PAST user-research studies for insights relevant to a question.

    Use this to answer questions about what users have said across previous
    studies (for example: 'what have users said about confusing instructions?').

    Args:
        query: A focused natural-language question or topic to search for.

    Returns:
        The most relevant snippets from past studies, each tagged with the study
        it came from, or a message saying nothing relevant was found.
    """
    col = get_collection()
    if col.count() == 0:
        return "Research memory is empty. Run ingest_memory.py first."
    res = col.query(query_texts=[query], n_results=4)
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    if not docs:
        return "No relevant past research found."
    return "\n\n".join(
        f"[from study: {m.get('study', '?')}]\n{d}" for d, m in zip(docs, metas)
    )
