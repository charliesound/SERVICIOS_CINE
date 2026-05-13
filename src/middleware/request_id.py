from __future__ import annotations

import uuid
from typing import Callable

from fastapi import Request, Response

from core.config import get_settings


async def request_id_middleware(request: Request, call_next: Callable) -> Response:
    """Ensure every request has a correlation ID.

    - Reads X-Request-ID from the incoming request header (if present).
    - Generates a UUID4 otherwise.
    - Stores it in ``request.state.request_id``.
    - Echoes it back in the response header.
    """
    header_name = get_settings().request_id_header
    rid = request.headers.get(header_name) or uuid.uuid4().hex
    request.state.request_id = rid

    response: Response = await call_next(request)
    response.headers[header_name] = rid
    return response
