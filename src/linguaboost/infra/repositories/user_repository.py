from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from linguaboost.infra.db.models import User, UserStats


async def get_user_by_telegram_id(session: AsyncSession, telegram_user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_user_id == telegram_user_id))
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    *,
    telegram_user_id: int,
    telegram_username: str | None,
) -> User:
    user = User(
        telegram_user_id=telegram_user_id,
        telegram_username=telegram_username,
        onboarding_step="timezone",
    )
    session.add(user)
    await session.flush()
    return user


async def ensure_user_stats(session: AsyncSession, user_id) -> UserStats:
    result = await session.execute(select(UserStats).where(UserStats.user_id == user_id))
    stats = result.scalar_one_or_none()
    if stats is None:
        stats = UserStats(user_id=user_id)
        session.add(stats)
        await session.flush()
    return stats
