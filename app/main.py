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
def admin_route_redirect():
    """Direct route for typing /admin in browser to access admin login/portal."""
    return RedirectResponse(url="/login.html?redirect=/admin_portal/index.html")


# Mount Static Files for HTML/CSS/JS Storefront
app.mount("/", StaticFiles(directory="static", html=True), name="static")
