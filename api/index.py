import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.main import app as fastapi_app
from fastapi import Request
from fastapi.responses import JSONResponse

@fastapi_app.get("/api/test-debug")
@fastapi_app.get("/test-debug")
def test_debug(request: Request):
    return {
        "path": request.scope.get("path"),
        "headers": {k.decode("latin-1"): v.decode("latin-1") for k, v in request.scope.get("headers", []) if "cookie" not in k.decode("latin-1").lower() and "auth" not in k.decode("latin-1").lower()}
    }

app = fastapi_app
