from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# SQLite connection string: threadcraft.db
# check_same_thread=False allows FastAPI multi-threaded requests with SQLite
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that provides a clean DB session per request and closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
