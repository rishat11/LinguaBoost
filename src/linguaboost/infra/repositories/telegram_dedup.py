from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from linguaboost.infra.db.models import TelegramProcessedUpdate


async def claim_telegram_update(
    session_factory: async_sessionmaker[AsyncSession],
    update_id: int,
) -> bool:
    """True — первый раз видим update_id и записали; False — дубликат webhook."""
    async with session_factory() as session:
        session.add(TelegramProcessedUpdate(update_id=update_id))
        try:
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False
