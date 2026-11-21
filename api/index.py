import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from app.main import app
except Exception as e:
    import traceback
    err_msg = str(e)
    err_tb = traceback.format_exc()
    print("FATAL: Error importing app.main in api/index.py:", err_tb)
    
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="S4 Fashions - Diagnostics")
    
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    async def debug_error_fallback(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Serverless Function Startup Failed",
                "message": err_msg,
                "traceback": err_tb.splitlines()
            }
        )
