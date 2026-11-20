from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.db.session import engine, Base
from app.routers import auth, products, orders, admin
from app.middleware.error_handlers import (
    rate_limit_exceeded_handler,
    http_exception_handler,
    validation_exception_handler,
    global_unhandled_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema exists on startup
    Base.metadata.create_all(bind=engine)
    yield


limiter = Limiter(key_func=get_remote_address, default_limits=[settings.DEFAULT_RATE_LIMIT])

app = FastAPI(
    title=settings.APP_NAME,
    description="Abuse-Resistant REST API & Storefront for Men, Women & Kids Apparel. Demonstrating CWE-89, CWE-639, CWE-209, CWE-347, and CWE-307 mitigations.",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter

# CORS Middleware (Restricts origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# No-Cache Middleware for Static Assets (Prevents stale cached scripts during development)
@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    path = request.url.path.lower()
    if path.endswith((".js", ".css", ".html")) or path == "/" or "static" in path:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Global Security Exception Handlers (CWE-209 & Rate Limiting)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_unhandled_exception_handler)

from fastapi.responses import RedirectResponse

# Include API Routers under /api/v1
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/admin")
@app.get("/admin/")
@app.get("/admin.html")
@app.get("/admin/login")
def admin_route_redirect():
    """Direct route for typing /admin in browser to access admin login/portal."""
    return RedirectResponse(url="/admin_portal/login.html")


@app.get("/admin/register")
def admin_register_redirect():
    """Direct route for admin registration."""
    return RedirectResponse(url="/admin_portal/register.html")


# Mount Static Files for HTML/CSS/JS Storefront with robust absolute path resolution
import os
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if not os.path.exists(STATIC_DIR):
    STATIC_DIR = "static"

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
