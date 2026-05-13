"""
ComfySearch — Semantic Search Engine for ComfyUI Workflows in CID

Indexes all ComfyUI workflow JSON files from configured roots,
generates embeddings with sentence-transformers,
stores vectors in Qdrant,
and exposes search by natural language query.
"""

import json
import os
import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logger.warning("sentence-transformers no instalado. ComfySearch usará modo fallback.")

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False
    logger.warning("qdrant-client no instalado. ComfySearch usará modo fallback.")

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "comfy_workflows")

WORKFLOW_ROOTS = os.getenv("COMFYSEARCH_ROOTS", "/opt/SERVICIOS_CINE/src/comfyui_workflows").split(",")
EMBEDDING_MODEL = os.getenv("COMFYSEARCH_EMBEDDING_MODEL", "all-MiniLM-L6-v2")


# ── Workflow Scanner ──────────────────────────────────────────────────────────

def scan_workflows(roots: list[str] = None) -> list[dict]:
    roots = roots or WORKFLOW_ROOTS
    items = []
    seen = set()

    for root in roots:
        root_path = Path(root.strip())
        if not root_path.exists():
            continue

        for ext in (".json", ".template.json"):
            for fpath in root_path.rglob(f"*{ext}"):
                if str(fpath) in seen:
                    continue
                seen.add(str(fpath))

                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning("ComfySearch: error leyendo %s: %s", fpath, e)
                    continue

                nodes = _extract_nodes(data)
                wf_id = hashlib.md5(str(fpath).encode()).hexdigest()[:16]
                name = fpath.stem.replace(".template", "")
                tags = _auto_tags(name, nodes)
                summary = _make_summary(name, nodes, tags)

                items.append({
                    "id": wf_id,
                    "name": name,
                    "path": str(fpath.absolute()),
                    "nodes": nodes,
                    "tags": tags,
                    "summary": summary,
                    "backend": _detect_backend(nodes, fpath),
                })
    return items


def _extract_nodes(data: dict) -> list[str]:
    nodes = set()
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, dict) and "class_type" in val:
                nodes.add(val["class_type"])
            elif isinstance(val, dict):
                for subkey, subval in val.items():
                    if isinstance(subval, dict) and "class_type" in subval:
                        nodes.add(subval["class_type"])
        if "nodes" in data and isinstance(data["nodes"], list):
            for node in data["nodes"]:
                if isinstance(node, dict) and "type" in node:
                    nodes.add(node["type"])
    return sorted(nodes)


def _auto_tags(name: str, nodes: list[str]) -> list[str]:
    tags = set()
    lower = name.lower()
    keyword_map = {
        "storyboard": "storyboard", "sdxl": "sdxl", "flux": "flux",
        "wan": "wan", "ltx": "ltxv", "video": "video", "img2vid": "i2v",
        "t2i": "t2i", "upscale": "restauracion", "restoration": "restauracion",
        "audio": "audio", "tts": "tts", "dubbing": "dubbing", "lipsync": "lipsync",
        "voice": "voice_clone", "clone": "voice_clone", "deinterlace": "restauracion",
        "character": "personaje", "compositing": "composicion",
    }
    for kw, tag in keyword_map.items():
        if kw in lower:
            tags.add(tag)
    for node in nodes:
        node_lower = node.lower()
        if "checkpoint" in node_lower and "sdxl" in node_lower:
            tags.add("sdxl")
        if "wan" in node_lower:
            tags.add("wan")
        if "ltx" in node_lower:
            tags.add("ltxv")
        if "saveaudio" in node_lower or "texttospeech" in node_lower:
            tags.add("audio")
            tags.add("tts")
        if "voiceclone" in node_lower:
            tags.add("voice_clone")
            tags.add("dubbing")
        if "wav2lip" in node_lower:
            tags.add("lipsync")
            tags.add("dubbing")
    return sorted(tags)


def _make_summary(name: str, nodes: list[str], tags: list[str]) -> str:
    node_str = ", ".join(nodes[:10])
    tag_str = ", ".join(tags)
    return f"Workflow '{name}' con nodos {node_str}. Tags: {tag_str}."


def _detect_backend(nodes: list[str], fpath: Path) -> str:
    node_lower = " ".join(n.lower() for n in nodes)
    if any(kw in node_lower for kw in ("texttospeech", "saveaudio", "voiceclone", "wav2lip", "speechtotext")):
        return "dubbing"
    if any(kw in node_lower for kw in ("wan", "ltx", "video")):
        return "video"
    if "upscale" in str(fpath).lower() or "deinterlace" in str(fpath).lower():
        return "lab"
    return "still"


# ── Embedding ─────────────────────────────────────────────────────────────────

class Embedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None and HAS_SENTENCE_TRANSFORMERS:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, text: str) -> list[float]:
        if self.model:
            return self.model.encode(text).tolist()
        return [0.0] * 384

    @property
    def dim(self) -> int:
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        return 384


# ── Qdrant Store ──────────────────────────────────────────────────────────────

class QdrantStore:
    def __init__(self, host: str = QDRANT_HOST, port: int = QDRANT_PORT, collection: str = COLLECTION_NAME):
        self.collection = collection
        self.client = QdrantClient(host=host, port=port) if HAS_QDRANT else None

    def ensure_collection(self, dim: int):
        if not self.client:
            return
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def ingest(self, items: list[dict], embedder: Embedder):
        if not self.client:
            logger.warning("Qdrant no disponible, skip ingest")
            return
        self.ensure_collection(embedder.dim)
        points = []
        for i, item in enumerate(items):
            text = f"{item['name']}. {item['summary']}. Tags: {', '.join(item['tags'])}. Nodes: {', '.join(item['nodes'][:20])}"
            vec = embedder.encode(text)
            points.append(PointStruct(id=i, vector=vec, payload=item))
        self.client.upsert(collection_name=self.collection, points=points)
        logger.info("ComfySearch: indexados %d workflows en Qdrant", len(points))

    def search(self, query: str, embedder: Embedder, top_k: int = 8) -> list[dict]:
        if not self.client:
            return []
        vector = embedder.encode(query)
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
        )
        results = []
        for h in hits:
            payload = h.payload or {}
            results.append({
                "id": payload.get("id"),
                "name": payload.get("name"),
                "path": payload.get("path"),
                "summary": payload.get("summary"),
                "tags": payload.get("tags", []),
                "nodes": payload.get("nodes", []),
                "backend": payload.get("backend", "still"),
                "score": round(h.score, 4),
            })
        return results


# ── Singleton ─────────────────────────────────────────────────────────────────

_embedder: Optional[Embedder] = None
_store: Optional[QdrantStore] = None


def get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder


def get_store() -> QdrantStore:
    global _store
    if _store is None:
        _store = QdrantStore()
    return _store


def index_all():
    items = scan_workflows()
    embedder = get_embedder()
    store = get_store()
    store.ingest(items, embedder)
    return len(items)
