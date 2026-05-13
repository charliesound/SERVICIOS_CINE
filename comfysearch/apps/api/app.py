"""
ComfySearch API — Buscador semántico de workflows de ComfyUI.

Endpoints:
  POST /search         Búsqueda semántica de workflows
  GET  /workflow/<id>  Detalle de workflow por ID
  POST /run/<id>       Ejecutar workflow en ComfyUI
  POST /reindex        Reindexar todos los workflows
  GET  /health         Health check
"""

import json
import os
import logging
from pathlib import Path

from flask import Flask, request, jsonify, render_template
import yaml

from services.workflow_parser import parse_workflow
from services.embedder import Embedder
from services.qdrant_store import QdrantStore
from services.comfy_client import run_workflow, resolve_url

# ── Config ────────────────────────────────────────────────────────────────────

app = Flask(__name__,
    template_folder=Path(__file__).parent.parent / "web" / "templates",
    static_folder=Path(__file__).parent.parent / "web" / "static",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("comfysearch")

config_path = os.getenv("COMFYSEARCH_CONFIG", "config/settings.yaml")
with open(config_path, "r", encoding="utf-8") as f:
    settings = yaml.safe_load(f)

qdrant_cfg = settings.get("qdrant", {})
embed_cfg = settings.get("embedding", {})
search_cfg = settings.get("search", {})
comfyui_cfg = settings.get("comfyui", {})

store = QdrantStore(
    host=qdrant_cfg.get("host", "localhost"),
    port=qdrant_cfg.get("port", 6333),
    collection=qdrant_cfg.get("collection", "comfy_workflows"),
)
embedder = Embedder(
    provider=embed_cfg.get("provider", "sentence_transformers"),
    model=embed_cfg.get("model", "all-MiniLM-L6-v2"),
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_workflow_roots() -> list[str]:
    roots_path = os.getenv("COMFYSEARCH_ROOTS", "config/workflow_roots.yaml")
    try:
        with open(roots_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return cfg.get("roots", [])
    except Exception:
        return os.getenv("WORKFLOW_ROOTS", "").split(",")


def scan_all_workflows() -> list[dict]:
    roots = load_workflow_roots()
    ignore_patterns = ["/archive/", "/deprecated/"]
    items = []
    seen = set()

    for root in roots:
        root_path = Path(root.strip())
        if not root_path.exists():
            continue
        for fpath in root_path.rglob("*.json"):
            if any(p in str(fpath) for p in ignore_patterns):
                continue
            if str(fpath) in seen:
                continue
            seen.add(str(fpath))
            parsed = parse_workflow(str(fpath))
            if parsed:
                items.append(parsed)

    return items


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    count = store.count()
    return render_template("index.html", count=count)


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "indexed": store.count(),
        "embedding": embedder.model_name,
    })


@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "query vacía"}), 400

    top_k = data.get("top_k", search_cfg.get("top_k", 8))
    filters = data.get("filters")

    results = store.search(query, embedder, top_k=top_k, filters=filters)

    return jsonify({
        "query": query,
        "total": len(results),
        "results": results,
    })


@app.route("/workflow/<workflow_id>")
def get_workflow(workflow_id: str):
    payload = store.get_by_id(workflow_id)
    if not payload:
        return jsonify({"error": "workflow no encontrado"}), 404

    # Intentar cargar el JSON real
    workflow_json = None
    path = payload.get("path")
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            workflow_json = json.load(f)

    return jsonify({
        "metadata": payload,
        "workflow": workflow_json,
    })


@app.route("/run/<workflow_id>", methods=["POST"])
def execute_workflow(workflow_id: str):
    payload = store.get_by_id(workflow_id)
    if not payload:
        return jsonify({"error": "workflow no encontrado"}), 404

    path = payload.get("path")
    if not path or not os.path.exists(path):
        return jsonify({"error": f"archivo JSON no encontrado: {path}"}), 404

    backend = payload.get("backend", "still")
    params = request.get_json() or {}

    try:
        result = run_workflow(path, backend=backend, params=params)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error ejecutando workflow {workflow_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/reindex", methods=["POST"])
def reindex():
    items = scan_all_workflows()
    count = store.ingest(items, embedder)
    return jsonify({"status": "ok", "indexed": count})


@app.route("/scan", methods=["GET"])
def scan():
    items = scan_all_workflows()
    return jsonify({"total": len(items), "workflows": items})


@app.route("/stats", methods=["GET"])
def stats():
    return jsonify({
        "indexed": store.count(),
        "embedding_model": embedder.model_name,
        "comfyui_instances": {
            "still": resolve_url("still"),
            "video": resolve_url("video"),
            "dubbing": resolve_url("dubbing"),
            "lab": resolve_url("lab"),
        },
    })


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5055"))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    logger.info("ComfySearch arrancando en %s:%s", host, port)
    logger.info("Qdrant: %s:%s | Colección: %s",
                qdrant_cfg.get("host"), qdrant_cfg.get("port"), qdrant_cfg.get("collection"))

    # Auto-index en primer arranque
    count = store.count()
    if count == 0:
        logger.info("Primer arranque — indexando workflows...")
        items = scan_all_workflows()
        if items:
            count = store.ingest(items, embedder)
            logger.info("Indexados %d workflows", count)

    app.run(host=host, port=port, debug=debug)
