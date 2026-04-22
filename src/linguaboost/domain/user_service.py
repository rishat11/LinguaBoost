from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from linguaboost.adapters.clock import Clock
from linguaboost.infra.db.models import User
from linguaboost.infra.repositories import user_repository


class UserService:
    def __init__(self, session: AsyncSession, clock: Clock) -> None:
        self._session = session
        self._clock = clock

    async def get_or_create_on_start(
        self,
        *,
        telegram_user_id: int,
        telegram_username: str | None,
    ) -> User:
        user = await user_repository.get_user_by_telegram_id(self._session, telegram_user_id)
        if user is None:
            user = await user_repository.create_user(
                self._session,
                telegram_user_id=telegram_user_id,
                telegram_username=telegram_username,
            )
        return user

    async def set_timezone(self, user: User, timezone_name: str) -> None:
        user.timezone = timezone_name
        user.onboarding_step = "level"

    async def set_level_and_complete(self, user: User, level: str) -> None:
        user.level = level
        user.onboarding_step = None
        user.onboarding_completed_at = datetime.now(timezone.utc)
        await user_repository.ensure_user_stats(self._session, user.id)
