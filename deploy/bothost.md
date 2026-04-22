# Деплой LinguaBoost на Bothost

Платформа: [Bothost](https://bothost.ru) — контейнер, Git‑деплой, HTTPS для webhook.

## Стек хранения (текущий код)

Одна **SQLite** (файл на диске) + dedup webhook в той же БД. **Redis и PostgreSQL не используются.**

На тарифе **Basic** подключите **Volume** к каталогу с БД (в Docker-образе по умолчанию это **`/app/data`**, файл `linguaboost.db` создаётся при первом старте после миграций).

## 1. Репозиторий и Dockerfile

В корне **`Dockerfile`** и **`requirements.txt`**: сначала ставятся зависимости из `requirements.txt`, затем пакет `linguaboost` (`pip install . --no-deps`). При старте: `/app/data`, `alembic upgrade head`, затем **`uvicorn`**.

Переменная **`PORT`** пробрасывается платформой; при отсутствии используется `8000`.

### Ошибка `ModuleNotFoundError: No module named 'fastapi'`

Обычно значит, что **не установлены зависимости** или запуск идёт «голым» `python` по пути `/app/src/...` без `pip install`.

Сделайте так:

1. В панели включите деплой через **Dockerfile** (или шаг установки: `pip install -r requirements.txt && pip install .`).
2. **Команда запуска** должна быть через установленный пакет, например:  
   `uvicorn linguaboost.app.main:app --host 0.0.0.0 --port ${PORT:-8000}`  
   Не используйте `python /app/src/linguaboost/app/main.py` как точку входа — зависимости могут не подхватиться.
3. Пересоберите образ / повторите деплой после пуша в репозиторий.

В коде есть **авто-установка зависимостей** при первом импорте, если нет `fastapi`, а рядом с проектом лежат `requirements.txt` и `pyproject.toml` (типичный случай «запуск из `/app/src` без `pip install»`). Отключить: переменная **`LINGUABOOST_SKIP_DEPS_BOOTSTRAP=1`**.

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
