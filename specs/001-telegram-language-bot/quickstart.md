# Quickstart: локальная разработка

**Дата**: 2026-04-22

## Переменные окружения

| Переменная | Назначение |
|------------|------------|
| `BOT_TOKEN` | Telegram BotFather |
| `WEBHOOK_SECRET` | Секрет в query webhook |
| `DATABASE_URL` | опционально; по умолчанию `sqlite+aiosqlite:///./data/linguaboost.db` (каталог `data/` создайте вручную или через приложение) |
| `LOG_LEVEL` | опционально, `INFO` |
| `LLM_ENABLED` / `LLM_API_KEY` / `LLM_BASE_URL` | опционально |

**PostgreSQL и Redis не требуются** (текущая ветка кода).

Секреты не коммитить; `.env` локально.

## Запуск

```bash
mkdir -p data
alembic upgrade head
uvicorn linguaboost.app.main:app --reload --port 8000
```

Webhook: `https://<host>/telegram/webhook?secret=<WEBHOOK_SECRET>`.

## Тесты

```bash
pytest -q
```
