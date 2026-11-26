import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "ThreadCraft Apparel API"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # JWT Settings (Pinned algorithm CWE-347, loaded from env CWE-798)
    SECRET_KEY: str = "default-unsafe-dev-secret-key-must-be-replaced-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days active session
    ADMIN_INVITE_SECRET: str = "s4-admin-secret-2026"

    # Database
    DATABASE_URL: str = "sqlite:///./threadcraft.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().strip("'\"")
            # If protocol prefix was accidentally truncated or altered during copy-paste
            if not v.startswith(("postgresql", "sqlite")):
                if "@" in v and "neon.tech" in v:
                    # Restore protocol
                    parts = v.split("@", 1)
                    creds = parts[0].lstrip("1.").strip()
                    host_part = parts[1].strip()
                    if ":" in creds:
                        user, pwd = creds.split(":", 1)
                    else:
                        user, pwd = "neondb_owner", creds
                    v = f"postgresql+psycopg2://{user}:{pwd}@{host_part}"
            elif v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+psycopg2://", 1)
            elif v.startswith("postgresql://") and not v.startswith("postgresql+"):
                v = v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    # Rate Limiting (SlowAPI)
    DEFAULT_RATE_LIMIT: str = "60/minute"
    AUTH_RATE_LIMIT: str = "5/minute"
    CHECKOUT_RATE_LIMIT: str = "10/minute"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
