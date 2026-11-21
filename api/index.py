import os
import sys
import urllib.parse

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.main import app as fastapi_app


class VercelASGIAdapter:
    """
    Handles Vercel serverless request path rewriting.
    Vercel passes sub-paths via query parameters ('match', '1', or 'path')
    or sets path to '/api' or '/api/index.py'.
    This middleware reconstructs the clean FastAPI path.
    """
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            path = scope.get("path", "")
            query_string = scope.get("query_string", b"").decode("latin-1")
            query_params = urllib.parse.parse_qs(query_string)

            subpath = None
            for key in ("match", "1", "path"):
                if key in query_params:
                    subpath = query_params[key][0]
                    break

            if subpath:
                clean_subpath = subpath.lstrip("/")
                if clean_subpath.startswith("api/"):
                    new_path = f"/{clean_subpath}"
                elif clean_subpath in ("docs", "openapi.json", "redoc"):
                    new_path = f"/{clean_subpath}"
                else:
                    new_path = f"/api/{clean_subpath}"
                scope["path"] = new_path
                scope["raw_path"] = new_path.encode("latin-1")
            elif path.startswith("/api/index.py"):
                remainder = path.replace("/api/index.py", "", 1)
                scope["path"] = remainder or "/"
                scope["raw_path"] = (remainder or "/").encode("latin-1")

        await self.asgi_app(scope, receive, send)


app = VercelASGIAdapter(fastapi_app)
