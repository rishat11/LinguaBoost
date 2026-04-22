import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from linguaboost.adapters.clock import SystemClock
from linguaboost.app.logging import safe_log_extra
from linguaboost.bot.keyboards.main_menu import level_keyboard, main_reply_keyboard, timezone_keyboard
from linguaboost.domain.user_service import UserService

router = Router(name="start")
log = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    svc = UserService(session, SystemClock())
    user = await svc.get_or_create_on_start(
        telegram_user_id=message.from_user.id,
        telegram_username=message.from_user.username,
    )
    log.info(
        "start",
        extra=safe_log_extra(telegram_user_id=message.from_user.id, step=user.onboarding_step),
    )
    if user.onboarding_completed_at is not None:
        await message.answer(
            "С возвращением! Выберите действие в меню.",
            reply_markup=main_reply_keyboard(),
        )
        return
    if user.onboarding_step == "timezone":
        await message.answer(
            "Привет! Выберите ваш часовой пояс — так мы корректно посчитаем «день» для уроков.",
            reply_markup=timezone_keyboard(),
        )
        return
    if user.onboarding_step == "level":
        await message.answer("Выберите уровень английского.", reply_markup=level_keyboard())
        return
    await message.answer(
        "Продолжим настройку. Выберите часовой пояс.",
        reply_markup=timezone_keyboard(),
    )


@router.callback_query(F.data.startswith("tz:"))
async def on_timezone(cb: CallbackQuery, session: AsyncSession) -> None:
    if cb.data is None or cb.message is None or cb.from_user is None:
        return
    tz = cb.data.removeprefix("tz:")
    svc = UserService(session, SystemClock())
    user = await svc.get_or_create_on_start(
        telegram_user_id=cb.from_user.id,
        telegram_username=cb.from_user.username,
    )
    await svc.set_timezone(user, tz)
    await cb.answer()
    await cb.message.answer("Отлично. Теперь уровень.", reply_markup=level_keyboard())


@router.callback_query(F.data.startswith("lvl:"))
async def on_level(cb: CallbackQuery, session: AsyncSession) -> None:
    if cb.data is None or cb.message is None or cb.from_user is None:
        return
    level = cb.data.removeprefix("lvl:")
    svc = UserService(session, SystemClock())
    user = await svc.get_or_create_on_start(
        telegram_user_id=cb.from_user.id,
        telegram_username=cb.from_user.username,
    )
    await svc.set_level_and_complete(user, level)
    await cb.answer()
    await cb.message.answer(
        f"Готово. Уровень: {level}. Добро пожаловать в LinguaBoost!",
        reply_markup=main_reply_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "LinguaBoost — мини-уроки и практика в чате.\n"
        "Команды: /start — меню и настройка, /help — эта справка.",
    )


@router.message(F.text == "Урок дня")
async def stub_lesson(message: Message) -> None:
    await message.answer("Урок дня появится в следующей итерации (US2).")


@router.message(F.text == "Практика")
async def stub_practice(message: Message) -> None:
    await message.answer("Практика появится в US3.")


@router.message(F.text == "Мой прогресс")
async def stub_progress(message: Message) -> None:
    await message.answer("Прогресс и streak — в US4.")


@router.message(F.text == "Настройки")
async def stub_settings(message: Message) -> None:
    await message.answer("Настройки — позже.")
