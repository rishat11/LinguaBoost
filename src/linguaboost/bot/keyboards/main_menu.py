from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def timezone_keyboard() -> InlineKeyboardMarkup:
    zones = [
        ("Europe/Moscow", "tz:Europe/Moscow"),
        ("Europe/Kaliningrad", "tz:Europe/Kaliningrad"),
        ("Asia/Yekaterinburg", "tz:Asia/Yekaterinburg"),
        ("UTC", "tz:UTC"),
    ]
    rows = [[InlineKeyboardButton(text=label, callback_data=data)] for label, data in zones]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def level_keyboard() -> InlineKeyboardMarkup:
    levels = ["A1", "A2", "B1", "B2"]
    rows = [[InlineKeyboardButton(text=L, callback_data=f"lvl:{L}")] for L in levels]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def main_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Урок дня")],
            [KeyboardButton(text="Практика"), KeyboardButton(text="Мой прогресс")],
            [KeyboardButton(text="Настройки")],
        ],
        resize_keyboard=True,
    )
