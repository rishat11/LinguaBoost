# Деплой LinguaBoost на Bothost

Платформа: [Bothost](https://bothost.ru) — контейнер, Git‑деплой, HTTPS для webhook.

## Что нужно по тарифу

Приложению нужны **PostgreSQL** и **Redis** (см. `plan.md`). На стороне Bothost ориентируйтесь на тариф с **PostgreSQL + Redis** (в маркетинговых материалах — линейка **Scale**) или подключите внешние БД и пропишите URL в переменных.

Бесплатный **Start (256 MB)** обычно **не** подходит под PostgreSQL + Redis + FastAPI в одном контейнере — только если вынести БД наружу и оставить в контейнере один процесс `uvicorn`.

## 1. Репозиторий и Dockerfile

В корне уже есть **`Dockerfile`**. В панели Bothost включите **свой Dockerfile** (см. их раздел «Кастомный Dockerfile» в документации).

Сборка ставит пакет `linguaboost` и при старте контейнера:

1. выполняет `alembic upgrade head` (если задан `DATABASE_URL`);
2. запускает `uvicorn linguaboost.app.main:app --host 0.0.0.0 --port $PORT`.

Платформа должна пробросить **`PORT`** (как у большинства PaaS). Если нет — по умолчанию используется `8000`.

## 2. Переменные окружения в панели Bothost

| Переменная | Назначение |
|------------|------------|
| `BOT_TOKEN` | токен от @BotFather |
| `DATABASE_URL` | `postgresql+asyncpg://USER:PASS@HOST:5432/DBNAME` |
| `REDIS_URL` | `redis://:PASS@HOST:6379/0` (как выдаёт Bothost или внешний Redis) |
| `WEBHOOK_SECRET` | длинная случайная строка; тот же секрет — в URL webhook |
| `LOG_LEVEL` | опционально, например `INFO` |

Не коммитьте секреты в Git.

## 3. Публичный URL и webhook Telegram

После деплоя у проекта будет HTTPS‑URL вида `https://bot-….bothost.ru` (точный формат смотрите в панели / раздел про веб‑приложения и домены).

Установите webhook (подставьте свои значения):

```text
https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<ваш-домен-bothost>/telegram/webhook?secret=<WEBHOOK_SECRET>
```

Путь и query **должны совпадать** с приложением: `POST /telegram/webhook`, параметр `secret`.

Проверка:

```text
https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo
```

## 4. Health check

`GET https://<ваш-домен>/health` → `{"status":"ok"}`.

## 5. Частые проблемы

- **401 на webhook** — неверный `secret` в query или прокси обрезает query; проверьте точный URL в `setWebhook`.
- **Ошибки миграций** — проверьте `DATABASE_URL`, доступ с контейнера к PostgreSQL, логи старта контейнера.
- **Нет Redis** — dedup и кеш не работают; приложение ожидает рабочий `REDIS_URL` (на старте вызывается `redis.ping()`).

При расхождении с фактической панелью Bothost ориентируйтесь на их актуальную документацию: [bothost.ru/docs](https://bothost.ru/docs).
