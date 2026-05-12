"""AILinkCinema — FastAPI application entry point.

Usage:
    python -m uvicorn app:app --host 0.0.0.0 --port 8000

The ``app`` instance is created by :func:`core.app_factory.create_app`.
"""
from core.app_factory import create_app

app = create_app()
