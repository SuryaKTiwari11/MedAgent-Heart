from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List

from .config import Settings
from .vector_database import VectorDatabase


@dataclass
class Agent:
    """Lightweight facade that wires vector DB utilities for higher-level use."""

    settings: Settings = field(default_factory=Settings.from_env)
    vector_db: VectorDatabase = field(init=False)

    def __post_init__(self):
        self.vector_db = VectorDatabase(settings=self.settings)

    def ingest_text(self, text: str, metadata: dict[str, Any] | None = None) -> int:
        """Split and ingest raw text into the configured vector store."""

        return self.vector_db.add_documents(text, metadata or {})

    def retrieve(self, query: str, top_k: int = 5) -> List[Any]:
        """Retrieve relevant documents for a query using the vector store."""

        retriever = self.vector_db.get_retriever(top_k=top_k)
        return retriever.get_relevant_documents(query)
