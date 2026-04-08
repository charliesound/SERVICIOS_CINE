from functools import lru_cache
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    from fastembed import TextEmbedding
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "fastembed is required. Install dependencies with services/embeddings/requirements.txt"
    ) from exc


MODEL_NAME = "BAAI/bge-small-en-v1.5"
EXPECTED_DIMENSIONS = 384


class EmbedRequest(BaseModel):
    text: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class EmbedResponse(BaseModel):
    ok: bool
    model: str
    dimensions: int
    vector: list[float]
    metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    ok: bool
    model: str
    dimensions: int


app = FastAPI(title="CINE AI Local Embeddings", version="1.0.0")


@lru_cache(maxsize=1)
def get_embedder() -> TextEmbedding:
    return TextEmbedding(model_name=MODEL_NAME)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        ok=True,
        model=MODEL_NAME,
        dimensions=EXPECTED_DIMENSIONS,
    )


@app.post("/embed", response_model=EmbedResponse)
def embed_text(payload: EmbedRequest) -> EmbedResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    embedder = get_embedder()
    vector = list(next(embedder.embed([text])))

    dimensions = len(vector)
    if dimensions != EXPECTED_DIMENSIONS:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected embedding size: {dimensions}. Expected {EXPECTED_DIMENSIONS}",
        )

    return EmbedResponse(
        ok=True,
        model=MODEL_NAME,
        dimensions=dimensions,
        vector=[float(value) for value in vector],
        metadata=payload.metadata,
    )