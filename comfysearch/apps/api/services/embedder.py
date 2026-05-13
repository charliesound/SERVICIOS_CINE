"""
embedder.py — Genera embeddings semánticos de workflows.

Soporta:
  - sentence-transformers (local, rápido)
  - Ollama embeddings (todo local, mejor calidad)
  - OpenAI embeddings (API, mejor calidad)
"""

from typing import Optional
import os


class Embedder:
    def __init__(self, provider: str = "sentence_transformers", model: str = "all-MiniLM-L6-v2"):
        self.provider = provider
        self.model_name = model
        self._model = None

    @property
    def model(self):
        if self._model is not None:
            return self._model
        if self.provider == "sentence_transformers":
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        elif self.provider == "ollama":
            self._model = self.model_name  # placeholder
        elif self.provider == "openai":
            import openai
            self._model = openai  # placeholder
        return self._model

    def encode(self, text: str) -> list[float]:
        if self.provider == "sentence_transformers":
            return self.model.encode(text).tolist()
        elif self.provider == "ollama":
            import requests
            resp = requests.post(
                f"{os.getenv('OLLAMA_URL', 'http://localhost:11434')}/api/embeddings",
                json={"model": self.model_name, "prompt": text},
            )
            return resp.json().get("embedding", [0.0] * 768)
        elif self.provider == "openai":
            resp = self.model.embeddings.create(
                model=self.model_name or "text-embedding-3-small",
                input=text,
            )
            return resp.data[0].embedding
        return [0.0] * 384

    @property
    def dim(self) -> int:
        if self.provider == "sentence_transformers":
            return self.model.get_sentence_embedding_dimension()
        elif self.provider == "ollama":
            return 768
        elif self.provider == "openai":
            return 1536
        return 384

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        if self.provider == "sentence_transformers":
            return self.model.encode(texts).tolist()
        return [self.encode(t) for t in texts]
