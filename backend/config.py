from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Typed view over environment-driven configuration."""

    pinecone_api_key: str | None
    pinecone_environment: str | None
    pinecone_index_name: str | None
    groq_api_key: str | None
    tavily_api_key: str | None
    embed_model: str
    doc_source_dir: str

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables with sensible defaults."""

        return cls(
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            pinecone_environment=os.getenv("PINECONE_ENVIRONMENT"),
            pinecone_index_name=os.getenv("PINECONE_INDEX_NAME"),
            groq_api_key=os.getenv("GROQ_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            embed_model=os.getenv(
                "EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
            ),
            doc_source_dir=os.getenv("DOC_SOURCE_DIR", "dataForRag"),
        )

    def require_vector_store(self) -> None:
        """Fail fast if required Pinecone settings are missing."""

        required = {
            "PINECONE_API_KEY": self.pinecone_api_key,
            "PINECONE_ENVIRONMENT": self.pinecone_environment,
            "PINECONE_INDEX_NAME": self.pinecone_index_name,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            formatted = ", ".join(sorted(missing))
            raise RuntimeError(
                f"Missing required Pinecone configuration: {formatted}. "
                "Set them in your environment or .env file."
            )


def validate_files_exist(paths: Iterable[str]) -> None:
    """Raise an error if any of the provided paths are missing."""

    missing = [path for path in paths if not os.path.exists(path)]
    if missing:
        formatted = ", ".join(sorted(missing))
        raise FileNotFoundError(f"Missing required files or folders: {formatted}")
