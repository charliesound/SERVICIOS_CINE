#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import uuid
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from services.project_document_rag_service import project_document_rag_service
from services.qdrant_service import qdrant_service


THEORY_COLLECTION = "cid_screenwriting_theory"


def _stable_point_id(*, source_file: str, chunk_index: int, chunk_text: str) -> str:
    seed = f"{source_file}:{chunk_index}:{chunk_text[:80]}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))


def _read_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return ""


def _infer_metadata(path: Path) -> dict[str, str]:
    stem = path.stem
    parts = [part.strip() for part in re.split(r"[-_]+", stem) if part.strip()]
    author = parts[0] if parts else "unknown"
    title = " ".join(parts[1:]) if len(parts) > 1 else stem
    return {
        "author": author,
        "title": title,
        "chapter": "",
        "topic": "screenwriting_theory",
        "source_file": str(path),
    }


async def run_ingest(base_dir: Path) -> dict[str, Any]:
    files = sorted(
        [p for p in base_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".pdf", ".md", ".txt"}]
    )
    all_points: list[dict[str, Any]] = []

    for path in files:
        text = _read_text(path)
        chunks = project_document_rag_service._chunk_text(text)
        if not chunks:
            continue
        vectors, _ = await project_document_rag_service._embed_texts(chunks)
        meta = _infer_metadata(path)
        for index, chunk in enumerate(chunks):
            vector = vectors[index] if index < len(vectors) else project_document_rag_service._embed_text(chunk)
            point_id = _stable_point_id(
                source_file=meta["source_file"],
                chunk_index=index,
                chunk_text=chunk,
            )
            all_points.append(
                {
                    "id": point_id,
                    "vector": vector,
                    "payload": {
                        **meta,
                        "chunk_index": index,
                        "chunk_text": chunk,
                    },
                }
            )

    if not all_points:
        return {"files": len(files), "points": 0, "collection": THEORY_COLLECTION, "status": "no_content"}

    vector_size = len(all_points[0]["vector"])
    await qdrant_service.create_collection(name=THEORY_COLLECTION, vector_size=vector_size, distance="Cosine")
    ok = await qdrant_service.upsert_points(collection=THEORY_COLLECTION, points=all_points)
    return {
        "files": len(files),
        "points": len(all_points),
        "collection": THEORY_COLLECTION,
        "status": "ok" if ok else "failed",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest screenwriting theory documents into Qdrant")
    parser.add_argument(
        "--input",
        default="data/theory/screenwriting/",
        help="Input folder containing PDFs/MD/TXT",
    )
    args = parser.parse_args()
    import asyncio

    result = asyncio.run(run_ingest(Path(args.input)))
    print(result)


if __name__ == "__main__":
    main()
