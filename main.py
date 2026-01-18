"""Resilient root ASGI entrypoint.

This module exposes an `app` callable immediately so hosting platforms can
detect and bind to the service port even if `backend.main` requires heavy
dependencies that aren't available at import time. On first request the
wrapper attempts to import `backend.main` and delegate to its `app`.
"""

import os
from importlib import import_module
from typing import Optional

# Lazily populated real app and last import error
_real_app = None  # type: Optional[object]
_import_error: Optional[BaseException] = None


async def _load_real_app() -> None:
    global _real_app, _import_error
    if _real_app or _import_error:
        return
    try:
        mod = import_module("backend.main")
        _real_app = getattr(mod, "app")
    except Exception as e:  # keep the original exception for debugging
        _import_error = e


async def app(scope, receive, send):
    """ASGI wrapper that delegates to backend.main.app when available.

    - Handles `lifespan` events minimally so servers like uvicorn can start.
    - On `http` scopes, if import fails, returns 500 with the error message.
    """
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            msg_type = message.get("type")
            if msg_type == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif msg_type == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
            else:
                # ignore other lifespan messages
                continue

    # For other scopes, ensure real app is loaded (if possible)
    if _real_app is None and _import_error is None:
        await _load_real_app()

    if _real_app is not None:
        return await _real_app(scope, receive, send)  # type: ignore

    # If we reach here, importing backend failed — respond with 500 for HTTP
    if scope["type"] == "http":
        body = ("Backend import error: " + repr(_import_error)).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": 500,
                "headers": [[b"content-type", b"text/plain; charset=utf-8"]],
            }
        )
        await send({"type": "http.response.body", "body": body})
        return


if __name__ == "__main__":
    import uvicorn

    PORT = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, workers=1)
