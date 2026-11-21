from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        db_url = settings.DATABASE_URL
        connect_args = {}
        engine_kwargs = {"pool_pre_ping": True}
        if "sqlite" in db_url:
            connect_args["check_same_thread"] = False
        else:
            engine_kwargs["pool_recycle"] = 300
        _engine = create_engine(db_url, connect_args=connect_args, **engine_kwargs)
    return _engine


def get_sessionmaker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


class _LazyEngineProxy:
    def __getattr__(self, name):
        return getattr(get_engine(), name)


class _LazySessionLocalProxy:
    def __call__(self, *args, **kwargs):
        return get_sessionmaker()(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(get_sessionmaker(), name)


engine = _LazyEngineProxy()
SessionLocal = _LazySessionLocalProxy()


def get_db():
    """Dependency that provides a clean DB session per request and closes it after."""
    db = get_sessionmaker()()
    try:
        yield db
    finally:
        db.close()
