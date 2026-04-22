import pytest

from linguaboost.infra.redis.client import claim_update


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def set(self, name: str, value: str, nx: bool = False, ex: int | None = None) -> bool | None:
        if nx and name in self.store:
            return None
        self.store[name] = value
        return True


@pytest.mark.asyncio
async def test_claim_update_first_succeeds() -> None:
    r = FakeRedis()
    assert await claim_update(r, 42) is True


@pytest.mark.asyncio
async def test_claim_update_duplicate_fails() -> None:
    r = FakeRedis()
    assert await claim_update(r, 7) is True
    assert await claim_update(r, 7) is False
