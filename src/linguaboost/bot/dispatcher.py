from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from linguaboost.adapters.config import Settings
from linguaboost.bot.middlewares.db_session import DbSessionMiddleware
from linguaboost.bot.routers.start import router as start_router


def create_bot_and_dispatcher(
    settings: Settings,
    session_factory: async_sessionmaker[AsyncSession],
) -> tuple[Bot, Dispatcher]:
    bot = Bot(settings.bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_factory))
    dp.include_router(start_router)
    return bot, dp
