from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/linguaboost.db",
        description="Async SQLAlchemy URL, e.g. sqlite+aiosqlite:///./data/linguaboost.db",
    )
    webhook_secret: str
    log_level: str = "INFO"

    llm_enabled: bool = False
    llm_api_key: str | None = None
    llm_base_url: str | None = None

    @field_validator("log_level")
    @classmethod
    def upper_log_level(cls, v: str) -> str:
        return v.upper()

    @property
    def database_url_sync(self) -> str:
        url = self.database_url
        if "+aiosqlite" in url:
            return url.replace("+aiosqlite", "+pysqlite", 1)
        if "+asyncpg" in url:
            return url.replace("+asyncpg", "+psycopg", 1)
        return url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
