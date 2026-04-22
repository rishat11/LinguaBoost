import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from linguaboost.infra.db.base import Base
from linguaboost.infra.db import models  # noqa: F401
from linguaboost.infra.repositories.telegram_dedup import claim_telegram_update


@pytest.fixture
async def session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest.mark.asyncio
async def test_claim_update_first_succeeds(session_factory) -> None:
    assert await claim_telegram_update(session_factory, 42) is True


@pytest.mark.asyncio
async def test_claim_update_duplicate_fails(session_factory) -> None:
    assert await claim_telegram_update(session_factory, 7) is True
    assert await claim_telegram_update(session_factory, 7) is False
