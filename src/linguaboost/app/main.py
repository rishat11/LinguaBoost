from contextlib import asynccontextmanager

from fastapi import FastAPI

from linguaboost.adapters.config import get_settings
from linguaboost.app.logging import setup_logging
from linguaboost.app.state import AppState
from linguaboost.app.webhook import router as webhook_router
from linguaboost.bot.dispatcher import create_bot_and_dispatcher
from linguaboost.infra.db.session import create_engine, create_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    bot, dp = create_bot_and_dispatcher(settings, session_factory)
    app.state.lb = AppState(
        settings=settings,
        session_factory=session_factory,
        bot=bot,
        dp=dp,
    )
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(title="LinguaBoost", lifespan=lifespan)
app.include_router(webhook_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
