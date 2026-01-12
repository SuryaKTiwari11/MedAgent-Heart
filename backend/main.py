from __future__ import annotations

import argparse
from pathlib import Path

from .agent import Agent
from .config import Settings, validate_files_exist


def main():
    parser = argparse.ArgumentParser(description="MedAgent backend utilities")
    parser.add_argument(
        "--ingest",
        type=str,
        help="Path to a text file to ingest into the vector store",
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Free-text query to retrieve relevant documents",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return when querying",
    )

    args = parser.parse_args()

    settings = Settings.from_env()
    agent = Agent(settings=settings)

    if args.ingest:
        validate_files_exist([args.ingest])
        content = Path(args.ingest).read_text(encoding="utf-8")
        chunks = agent.ingest_text(content, metadata={"source": args.ingest})
        print(f"Ingested {chunks} chunks from {args.ingest}")

    if args.query:
        docs = agent.retrieve(args.query, top_k=args.top_k)
        for idx, doc in enumerate(docs, start=1):
            print(f"{idx}. {doc}")

    if not args.ingest and not args.query:
        parser.print_help()


if __name__ == "__main__":
    main()

