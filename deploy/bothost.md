# Деплой LinguaBoost на Bothost

Платформа: [Bothost](https://bothost.ru) — контейнер, Git‑деплой, HTTPS для webhook.

## Стек хранения (текущий код)

Одна **SQLite** (файл на диске) + dedup webhook в той же БД. **Redis и PostgreSQL не используются.**

На тарифе **Basic** подключите **Volume** к каталогу с БД (в Docker-образе по умолчанию это **`/app/data`**, файл `linguaboost.db` создаётся при первом старте после миграций).

## 1. Репозиторий и Dockerfile

В корне **`Dockerfile`**: при старте создаётся `/app/data`, выполняется `alembic upgrade head`, затем `uvicorn`.

Переменная **`PORT`** пробрасывается платформой; при отсутствии используется `8000`.

## 2. Переменные окружения

| Переменная | Назначение |
|------------|------------|
| `BOT_TOKEN` | токен от @BotFather |
| `WEBHOOK_SECRET` | секрет в URL webhook |
| `DATABASE_URL` | опционально; по умолчанию в коде `sqlite+aiosqlite:///./data/linguaboost.db` (в контейнере — под `/app/data`) |
| `LOG_LEVEL` | опционально, например `INFO` |

**`REDIS_URL` больше не нужен.**

Не коммитьте секреты в Git.

## 3. Webhook Telegram

HTTPS‑URL проекта, например `https://bot-….bothost.ru`:

```text
https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<ваш-домен-bothost>/telegram/webhook?secret=<WEBHOOK_SECRET>
```

Проверка: `getWebhookInfo`.

## 4. Health check

`GET https://<ваш-домен>/health` → `{"status":"ok"}`.

## 5. Тарифы Bothost

**Starter (0 ₽):** данные при перезапуске могут теряться без постоянного тома — для SQLite нежелательно.

**Basic / Pro:** используйте **постоянный диск (Volume)** для `/app/data`, чтобы файл БД сохранялся между деплоями.

Документация платформы: [bothost.ru/docs](https://bothost.ru/docs).
