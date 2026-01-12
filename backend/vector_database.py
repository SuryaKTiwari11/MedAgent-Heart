from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict
from .config import Settings

DEFAULT_DIMENSION = 384  # Fallback for MiniLM when dimension probing is not possible.


def _lazy_import_pinecone():
    try:
        from pinecone import Pinecone, ServerlessSpec
    except ImportError as exc:  # pragma: no cover - defensive guard
        raise ImportError(
            "Pinecone is not installed. Install with 'pip install pinecone-client'."
        ) from exc
    return Pinecone, ServerlessSpec


def _lazy_import_embeddings():
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError as exc:  # pragma: no cover - defensive guard
        raise ImportError(
            "Embedding support is missing. Install with 'pip install langchain-community "
            "sentence-transformers'."
        ) from exc
    return HuggingFaceEmbeddings


def _lazy_import_splitter():
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError as exc:  # pragma: no cover - defensive guard
        raise ImportError(
            "Text splitter is missing. Install with 'pip install langchain-text-splitters'."
        ) from exc
    return RecursiveCharacterTextSplitter


def _lazy_import_vectorstore():
    try:
        from langchain_pinecone import PineconeVectorStore
    except ImportError as exc:  # pragma: no cover - defensive guard
        raise ImportError(
            "Vector store integration is missing. Install with 'pip install langchain-pinecone'."
        ) from exc
    return PineconeVectorStore


@dataclass
class VectorDatabase:
    """Pinecone-backed vector store utilities with lazy dependency loading."""

    settings: Settings = field(default_factory=Settings.from_env)
    _pinecone: Any | None = field(init=False, default=None)
    _embeddings: Any | None = field(init=False, default=None)

    def _pinecone_client(self):
        self.settings.require_vector_store()
        if self._pinecone is not None:
            return self._pinecone

        Pinecone, _ = _lazy_import_pinecone()
        self._pinecone = Pinecone(api_key=self.settings.pinecone_api_key)
        return self._pinecone

    def _embedding_model(self):
        if self._embeddings is not None:
            return self._embeddings

        HuggingFaceEmbeddings = _lazy_import_embeddings()
        self._embeddings = HuggingFaceEmbeddings(model_name=self.settings.embed_model)
        return self._embeddings

    def _embedding_dimension(self) -> int:
        embedder = self._embedding_model()
        try:
            return len(embedder.embed_query("probe"))
        except Exception:  # pragma: no cover - fallback for unusual models
            return DEFAULT_DIMENSION

    def _ensure_index(self) -> Any:
        client = self._pinecone_client()
        _, ServerlessSpec = _lazy_import_pinecone()
        index_name = self.settings.pinecone_index_name
        existing = client.list_indexes().names()

        if index_name not in existing:
            client.create_index(
                name=index_name,
                dimension=self._embedding_dimension(),
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=self.settings.pinecone_environment,
                ),
            )

        return client.Index(index_name)

    def get_retriever(self, top_k: int = 5):
        """Return a LangChain retriever for the configured index."""

        if top_k <= 0:
            raise ValueError("top_k must be a positive integer.")

        PineconeVectorStore = _lazy_import_vectorstore()
        self._ensure_index()
        store = PineconeVectorStore(
            index_name=self.settings.pinecone_index_name,
            embedding=self._embedding_model(),
            namespace=None,
            pc=self._pinecone_client(),
        )
        return store.as_retriever(search_kwargs={"k": top_k})

    def add_documents(
        self,
        text_content: str,
        metadata: Dict[str, Any] | None = None,
        *,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> int:
        """Split and ingest raw text into the vector store.

        Returns the number of chunks written.
        """

        if not text_content or not text_content.strip():
            raise ValueError("Document content cannot be empty.")

        RecursiveCharacterTextSplitter = _lazy_import_splitter()
        PineconeVectorStore = _lazy_import_vectorstore()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,
        )

        meta = metadata or {}
        if not isinstance(meta, dict):
            raise TypeError("metadata must be a dictionary if provided.")

        docs = splitter.create_documents([text_content], metadatas=[meta])
        self._ensure_index()
        store = PineconeVectorStore(
            index_name=self.settings.pinecone_index_name,
            embedding=self._embedding_model(),
            namespace=None,
            pc=self._pinecone_client(),
        )
        store.add_documents(docs)

        return len(docs)
