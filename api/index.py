import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.main import app as fastapi_app


class VercelPathFixMiddleware:
    """
    Vercel rewrites (/(.*) -> /api/index.py) rewrite scope['path'] to '/api/index.py'.
    Vercel stores the true requested URL in the 'x-matched-path' header.
    This ASGI middleware restores the real URL path so FastAPI routes and static files match perfectly!
    """
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            headers = dict(scope.get("headers", []))
            matched_path = headers.get(b"x-matched-path", b"").decode("latin-1")
            if matched_path:
                clean_path = matched_path.split("?")[0]
                scope["path"] = clean_path
                scope["raw_path"] = clean_path.encode("latin-1")
        await self.asgi_app(scope, receive, send)


app = VercelPathFixMiddleware(fastapi_app)
