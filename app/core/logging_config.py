import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Ensure logs directory exists (safe against read-only serverless filesystems)
LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
try:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

USER_LOG_PATH = LOGS_DIR / "user.log"
ADMIN_LOG_PATH = LOGS_DIR / "admin.log"

# Log Formatters
USER_FORMAT = logging.Formatter(
    fmt="%(asctime)s | [%(levelname)s] | [USER-ACTIVITY] | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

ADMIN_FORMAT = logging.Formatter(
    fmt="%(asctime)s | [%(levelname)s] | [ADMIN-AUDIT] | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def _setup_logger(name: str, log_file: Path, formatter: logging.Formatter, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if reloaded
    if not logger.handlers:
        # File Handler (redirect to /tmp in serverless or fallback safely on read-only environments)
        try:
            target_file = log_file
            if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
                tmp_dir = Path("/tmp/logs")
                tmp_dir.mkdir(parents=True, exist_ok=True)
                target_file = tmp_dir / log_file.name

            file_handler = RotatingFileHandler(
                target_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            logger.addHandler(file_handler)
        except Exception:
            # Serverless read-only filesystem: continue safely with console handler
            pass

        # Console Handler (Streams directly into Vercel runtime logs)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

    logger.propagate = False
    return logger

# 1. Customer / User Activity Logger
user_logger = _setup_logger("app.user", USER_LOG_PATH, USER_FORMAT)

# 2. Administrator & Security Audit Logger
admin_logger = _setup_logger("app.admin", ADMIN_LOG_PATH, ADMIN_FORMAT)


def log_user_event(action: str, username: str, ip: str, details: str = "", level: str = "info"):
    """Logs customer activity: registration, login, cart, order placement."""
    msg = f"User='{username}' | IP='{ip}' | Action='{action}' | Details='{details}'"
    log_func = getattr(user_logger, level.lower(), user_logger.info)
    log_func(msg)


def log_admin_event(action: str, admin_user: str, ip: str, details: str = "", status: str = "SUCCESS", level: str = "info"):
    """Logs administrative & security audit events: product CRUD, category CRUD, order management, auth."""
    msg = f"Admin='{admin_user}' | IP='{ip}' | Action='{action}' | Status='{status}' | Details='{details}'"
    log_func = getattr(admin_logger, level.lower(), admin_logger.info)
    log_func(msg)
