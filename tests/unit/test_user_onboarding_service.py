import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from linguaboost.adapters.clock import FrozenClock
from linguaboost.domain.user_service import UserService
from linguaboost.infra.db.models import User


@pytest.mark.asyncio
async def test_set_timezone_moves_to_level_step() -> None:
    session = AsyncMock(spec=AsyncSession)
    clock = FrozenClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    svc = UserService(session, clock)
    user = User(
        id=uuid.uuid4(),
        telegram_user_id=99,
        telegram_username=None,
        timezone="Europe/Moscow",
        onboarding_step="timezone",
    )
    await svc.set_timezone(user, "Asia/Yekaterinburg")
    assert user.timezone == "Asia/Yekaterinburg"
    assert user.onboarding_step == "level"


@pytest.mark.asyncio
async def test_complete_onboarding_sets_timestamp_and_stats_called() -> None:
    session = AsyncMock(spec=AsyncSession)
    clock = FrozenClock(datetime(2026, 1, 2, tzinfo=timezone.utc))
    svc = UserService(session, clock)
    uid = uuid.uuid4()
    user = User(
        id=uid,
        telegram_user_id=100,
        telegram_username="tester",
        timezone="UTC",
        onboarding_step="level",
    )
    with pytest.MonkeyPatch.context() as mp:
        from linguaboost.domain import user_service as us_mod

        ensure = AsyncMock(return_value=None)
        mp.setattr(us_mod.user_repository, "ensure_user_stats", ensure)
        await svc.set_level_and_complete(user, "B1")
    assert user.level == "B1"
    assert user.onboarding_step is None
    assert user.onboarding_completed_at is not None
    ensure.assert_awaited_once()
