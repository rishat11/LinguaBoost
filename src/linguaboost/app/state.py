from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from linguaboost.adapters.clock import Clock, SystemClock
from linguaboost.adapters.config import Settings


@dataclass(slots=True)
class AppState:
    settings: Settings
    session_factory: async_sessionmaker[AsyncSession]
    bot: Bot
    dp: Dispatcher
    clock: Clock = SystemClock()
