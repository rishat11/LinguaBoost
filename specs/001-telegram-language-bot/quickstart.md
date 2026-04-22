# Quickstart: локальная разработка

**Дата**: 2026-04-22

## Переменные окружения (черновик)

| Переменная | Назначение |
|------------|------------|
| `BOT_TOKEN` | Telegram BotFather |
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/linguaboost` |
| `REDIS_URL` | `redis://localhost:6379/0` |
| `WEBHOOK_URL` | Публичный URL для `setWebhook` |
| `WEBHOOK_PATH` | Например `/telegram/webhook` |
| `WEBHOOK_SECRET` | Секрет в query/header |
| `LLM_ENABLED` | `0` / `1` |
| `LLM_API_KEY` | Если включено |
| `LOG_LEVEL` | `INFO` |

Секреты не коммитить; использовать `.env` локально (файл в `.gitignore`).

## Docker Compose (рекомендуется для dev)

Поднять **PostgreSQL** и **Redis**; приложение локально через `uv run` / `venv` для отладки breakpoints.

Пример сервисов (адаптировать порты):

- `postgres:15`
- `redis:7`

## Запуск (целевое состояние после реализации)

```bash
alembic upgrade head
uvicorn linguaboost.app.main:app --reload --port 8000
```

Telegram: настроить webhook на `https://<host>/<WEBHOOK_PATH>?secret=<WEBHOOK_SECRET>` или использовать ngrok для локальных тестов.

## Тесты

```bash
pytest -q
```

Интеграционные тесты — при наличии `docker compose -f compose.test.yml up -d`.
