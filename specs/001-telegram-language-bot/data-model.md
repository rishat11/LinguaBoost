# Модель данных: LinguaBoost MVP

**Дата**: 2026-04-22 | Спека: [spec.md](./spec.md)

## PostgreSQL: таблицы (черновик)

### `users`

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | Внутренний id |
| telegram_user_id | BIGINT UNIQUE NOT NULL | id пользователя Telegram |
| telegram_username | TEXT NULL | @username, опционально |
| ui_locale | TEXT NOT NULL DEFAULT 'ru' | MVP: ru |
| target_language | TEXT NOT NULL DEFAULT 'en' | Целевой язык (v1: en) |
| level | TEXT NOT NULL | Например A1/B1 — перечисление в коде |
| timezone | TEXT NOT NULL | IANA, напр. `Europe/Moscow` |
| onboarding_completed_at | TIMESTAMPTZ NULL | |
| reminders_enabled | BOOLEAN NOT NULL DEFAULT false | opt-in |
| reminder_local_time | TIME NULL | Предпочтительное локальное время |
| quiet_hours_start | TIME NULL | Начало тихих часов (опц.) |
| quiet_hours_end | TIME NULL | Конец тихих часов (опц.) |
| created_at / updated_at | TIMESTAMPTZ | |

### `user_deletion_requests`

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| requested_at | TIMESTAMPTZ | |
| processed_at | TIMESTAMPTZ NULL | В течение 30 дней |
| status | TEXT | pending / completed |

### `lesson_progress`

Фиксация прохождения **конкретного урока** из контент-пакета.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| user_id | UUID FK | |
| content_pack_version | TEXT NOT NULL | Версия пакета |
| lesson_id | TEXT NOT NULL | id урока в пакете |
| local_date | DATE NOT NULL | Дата «урока дня» в TZ пользователя |
| state | JSONB NOT NULL | Текущий шаг, ответы (минимально необходимое) |
| completed_at | TIMESTAMPTZ NULL | |
| UNIQUE(user_id, content_pack_version, local_date) | | Один активный «день» на версию пакета |

### `practice_sessions`

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| user_id | UUID FK | |
| scenario_id | TEXT NOT NULL | id сценария из пакета |
| state_machine_state | TEXT NOT NULL | Текущее состояние FSM сценария |
| context | JSONB NOT NULL DEFAULT '{}' | Служебный контекст |
| completed_at | TIMESTAMPTZ NULL | |
| updated_at | TIMESTAMPTZ | |

### `user_stats` (денормализация для UX)

| Поле | Тип | Описание |
|------|-----|----------|
| user_id | UUID PK FK | |
| streak_current | INT NOT NULL DEFAULT 0 | |
| streak_best | INT NOT NULL DEFAULT 0 | |
| lessons_completed | INT NOT NULL DEFAULT 0 | |
| last_activity_local_date | DATE NULL | Для streak-логики |

Индексы: `users(telegram_user_id)`, `lesson_progress(user_id, local_date)`, `practice_sessions(user_id) WHERE completed_at IS NULL` (частичный, если поддерживается).

## Redis: ключи (соглашения)

| Ключ / паттерн | Назначение | TTL |
|----------------|------------|-----|
| `dedup:telegram:update:{update_id}` | Идемпотентность webhook | 24–48 ч |
| `reminder:sent:{user_id}:{local_date}` | Не больше 1 напоминания за локальный день | до конца «дня» (оценка TTL) |
| `cache:lesson_day:{user_id}:{local_date}` | Опционально кеш агрегата «что показывать» | минуты |

При отказе Redis деградация: dedup можно временно отключить флагом (риск двойной обработки) или требовать Redis как обязательный для продакшена — зафиксировать в runbook.

## Контент-пакет (файлы)

Версионируемый артефакт (YAML/JSON) в репозитории или volume:

- `version`: строка semver/дата
- `lessons[]`: id, шаги (theory/exercise), ожидаемые ответы, подсказки
- `practice_scenarios[]`: id, переходы FSM, ожидаемые паттерны ответов

Связь с БД: `lesson_progress.content_pack_version` + `lesson_id`.
