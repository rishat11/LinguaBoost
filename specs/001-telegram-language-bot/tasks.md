# Tasks: Telegram-бот LinguaBoost

**Вход**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md), [research.md](./research.md), [contracts/openapi.yaml](./contracts/openapi.yaml)

**Формат**: `[ID] [P?] [US#] Описание` — **P** = можно параллелить (разные файлы, без жёсткой зависимости). **US1–US4** = пользовательские истории из спеки.

**Пути**: монолит в `src/linguaboost/` и `tests/` (как в plan.md).

---

## Phase 1: Setup (общая инфраструктура)

**Цель**: структура каталогов и зависимости под план.

- [ ] T001 Создать дерево `src/linguaboost/{app,bot,domain,infra,content,scheduler,adapters}` и пустые `__init__.py` по необходимости
- [ ] T002 [P] Обновить `pyproject.toml`: зависимости FastAPI, uvicorn, aiogram 3.x, SQLAlchemy[asyncio], asyncpg, Alembic, redis (async), APScheduler 4.x, pydantic-settings, PyYAML (или orjson + json для пакета — согласовать с content loader)
- [ ] T003 [P] Расширить `pyproject.toml` optional `dev`: pytest-asyncio, httpx, testcontainers (или маркер integration)
- [ ] T004 [P] Настроить Ruff под `src/linguaboost` в существующем `pyproject.toml` (include paths)

---

## Phase 2: Foundational (блокирует все US)

**Цель**: приложение, конфиг, логирование, БД, Redis, webhook — без продуктовой логики историй.

**Контрольная точка**: health + webhook принимает update; миграции применяются.

- [ ] T005 Реализовать `src/linguaboost/adapters/config.py` (Pydantic Settings): `BOT_TOKEN`, `DATABASE_URL`, `REDIS_URL`, `WEBHOOK_SECRET`, `LOG_LEVEL`, опционально `LLM_*`
- [ ] T006 [P] Реализовать `src/linguaboost/adapters/clock.py` — абстракция «текущее время» для тестов
- [ ] T007 Реализовать `src/linguaboost/app/logging.py` — структурные логи без секретов и полного текста сообщений пользователя
- [ ] T008 Реализовать `src/linguaboost/infra/db/session.py` — async engine, session factory
- [ ] T009 [P] Реализовать `src/linguaboost/infra/db/models.py` — SQLAlchemy-модели по [data-model.md](./data-model.md) (users, user_deletion_requests, lesson_progress, practice_sessions, user_stats)
- [ ] T010 Инициализировать Alembic в `src/linguaboost/infra/db/migrations/` и первая ревизия схемы
- [ ] T011 [P] Реализовать `src/linguaboost/infra/redis/client.py` — async Redis + helper `SET NX` для dedup
- [ ] T012 Реализовать `src/linguaboost/app/main.py` — FastAPI app, `GET /health`, lifespan-заготовка
- [ ] T013 Реализовать `src/linguaboost/app/webhook.py` — `POST /telegram/webhook`, проверка секрета, dedup по `update_id`, передача update в aiogram Dispatcher
- [ ] T014 Реализовать `src/linguaboost/bot/dispatcher.py` — сборка Dispatcher, Bot, роутер-заглушка `/start`
- [ ] T015 [P] Юнит-тест `tests/unit/test_webhook_dedup.py` — mock Redis: второй такой же update не обрабатывается

---

## Phase 3: User Story 1 — Онбординг и меню (P1) 🎯 MVP

**Спека**: US1 — профиль, языки/уровень, главное меню.

**Независимая проверка**: тестовый Telegram-аккаунт проходит `/start` → ответы → меню; в БД есть строка `users`.

### Тесты (US1)

- [ ] T016 [P] [US1] `tests/unit/test_user_onboarding_service.py` — создание пользователя, валидация шагов без Telegram
- [ ] T017 [P] [US1] `tests/integration/test_onboarding_flow.py` (опционально, docker) — репозиторий + сервис

### Реализация (US1)

- [ ] T018 [P] [US1] `src/linguaboost/infra/repositories/user_repository.py` — CRUD пользователя по `telegram_user_id`
- [ ] T019 [US1] `src/linguaboost/domain/user_service.py` — онбординг: шаги, сохранение timezone/level, `onboarding_completed_at`
- [ ] T020 [US1] `src/linguaboost/bot/routers/start.py` — FSM или пошаговые состояния с привязкой к домену
- [ ] T021 [US1] `src/linguaboost/bot/keyboards/main_menu.py` — главное меню (RU)
- [ ] T022 [US1] `src/linguaboost/bot/middlewares/user_context.py` — подгрузка пользователя в контекст хендлеров

**Контрольная точка**: US1 работает end-to-end с реальной БД.

---

## Phase 4: User Story 2 — Ежедневный мини-урок (P1)

**Спека**: US2 — урок дня, упражнения, продолжение после паузы, идемпотентность шага.

**Независимая проверка**: фикстурный контент-пакет; прохождение шагов; повторный ответ на тот же шаг не ломает прогресс.

### Тесты (US2)

- [ ] T023 [P] [US2] `tests/unit/test_content_catalog.py` — загрузка YAML/JSON из `src/linguaboost/content/fixtures/` (тестовый пакет)
- [ ] T024 [P] [US2] `tests/unit/test_lesson_engine.py` — переходы шагов, проверка ответов, resume

### Реализация (US2)

- [ ] T025 [P] [US2] `src/linguaboost/content/loader.py` — загрузка и валидация пакета (версия, lessons)
- [ ] T026 [P] [US2] Добавить MVP контент-пакет `src/linguaboost/content/packs/default_v1/` (1–2 урока для пилота)
- [ ] T027 [US2] `src/linguaboost/domain/lesson_service.py` — выбор урока на `local_date`, шаги, завершение, запись `lesson_progress`
- [ ] T028 [US2] `src/linguaboost/infra/repositories/lesson_repository.py`
- [ ] T029 [US2] `src/linguaboost/bot/routers/lessons.py` — команды/callback «Урок дня», отправка шагов, приём текстовых ответов
- [ ] T030 [US2] Идемпотентность шага урока: ключ в Redis или уникальный constraint + обработка повтора (согласовать с spec FR и edge cases)

**Контрольная точка**: US1 + US2 независимо проверяются; урок не теряется при рестарте (состояние в БД).

---

## Phase 5: User Story 3 — Практика в чате (P2)

**Спека**: US3 — сценарий FSM, только текст, выход с сохранением.

**Независимая проверка**: сценарий из 3–5 реплик в юнит-тесте без сети.

### Тесты (US3)

- [ ] T031 [P] [US3] `tests/unit/test_practice_scenario_engine.py` — переходы по ожидаемым ответам/веткам

### Реализация (US3)

- [ ] T032 [P] [US3] Расширить контент-пакет: `practice_scenarios` минимум один сценарий
- [ ] T033 [US3] `src/linguaboost/domain/practice_service.py` — движок FSM, сохранение `practice_sessions`
- [ ] T034 [US3] `src/linguaboost/infra/repositories/practice_repository.py`
- [ ] T035 [US3] `src/linguaboost/bot/routers/practice.py` — старт/шаг/выход; не-текстовые апдейты → вежливый отказ (spec edge cases)

**Контрольная точка**: практика не ломает US1/US2.

---

## Phase 6: User Story 4 — Прогресс, streak, напоминания (P3)

**Спека**: US4 — статистика, opt-in напоминания, не более 1/день, тихие часы.

**Независимая проверка**: после завершения урока обновляются счётчики; тест планировщика с мок Clock и mock Bot.send_message.

### Тесты (US4)

- [ ] T036 [P] [US4] `tests/unit/test_progress_streak.py` — границы локального дня, streak
- [ ] T037 [P] [US4] `tests/unit/test_reminder_eligibility.py` — окно ±30 мин, тихие часы, не более одного срабатывания за день

### Реализация (US4)

- [ ] T038 [US4] `src/linguaboost/domain/progress_service.py` — обновление `user_stats` при завершении урока/активности
- [ ] T039 [US4] `src/linguaboost/domain/reminder_service.py` — выбор кандидатов, идемпотентная отправка
- [ ] T040 [US4] `src/linguaboost/scheduler/jobs.py` — регистрация задач APScheduler (тик напоминаний)
- [ ] T041 [US4] Подключить scheduler в `src/linguaboost/app/main.py` lifespan (start/stop)
- [ ] T042 [US4] `src/linguaboost/bot/routers/progress.py` — экран «Мой прогресс»; настройки напоминаний

**Контрольная точка**: напоминания не дублируются при рестарте (Redis/БД).

---

## Phase 7: Опционально — LLM и удаление данных

- [ ] T043 [P] `src/linguaboost/adapters/llm_client.py` + `src/linguaboost/domain/llm_service.py` — за фичефлагом, таймауты
- [ ] T044 [P] `tests/unit/test_llm_service_off.py` — при `LLM_ENABLED=0` вызовы не идут в сеть
- [ ] T045 `src/linguaboost/domain/gdpr_service.py` — заявка на удаление, статусы
- [ ] T046 `src/linguaboost/bot/routers/settings.py` — поток «удалить мои данные»
- [ ] T047 `src/linguaboost/scheduler/jobs.py` — housekeeping обработки deletion requests (если не сделано в T040)

---

## Phase 8: Polish & cross-cutting

- [ ] T048 [P] Обновить `specs/001-telegram-language-bot/quickstart.md` при расхождении с фактическими командами
- [ ] T049 [P] `docker-compose.yml` в корне — только postgres+redis для dev (при необходимости)
- [ ] T050 Проверка соответствия `contracts/openapi.yaml` реальным маршрутам
- [ ] T051 Прогон `ruff check` / `pytest` в CI или локальный чеклист релиза (секреты, логи)

---

## Зависимости и порядок

| Фаза | Зависит от | Блокирует |
|------|------------|-----------|
| Phase 1 | — | Phase 2 |
| Phase 2 | Phase 1 | US1–US4 |
| Phase 3 (US1) | Phase 2 | желательно перед US2 (профиль) |
| Phase 4 (US2) | Phase 3 | — |
| Phase 5 (US3) | Phase 3 (минимум пользователь) | — |
| Phase 6 (US4) | Phase 4 (урок для streak) | — |
| Phase 7–8 | нужные US | релиз |

**Параллельно после Phase 2**: US3 частично параллелится с US2, если US1 готов; US4 логично после рабочего урока (US2).

---

## Параллельный пример

```text
# После Phase 2:
T018 user_repository + T023 content_catalog_loader (разные области)

# Тесты одной истории:
T023 + T024 (US2 unit tests) до T027–T029
```

---

## Следующий шаг

**`/speckit.implement`** — выполнять задачи по порядку с чекпоинтами; или взять Phase 1–2 в работу первыми.
