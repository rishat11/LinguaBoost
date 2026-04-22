import logging
from typing import Any

from aiogram.types import Update
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from linguaboost.app.state import AppState
from linguaboost.infra.repositories.telegram_dedup import claim_telegram_update

router = APIRouter(prefix="/telegram", tags=["telegram"])
log = logging.getLogger(__name__)


@router.post("/webhook")
async def telegram_webhook(request: Request, secret: str | None = None) -> Response:
    lb: AppState = request.app.state.lb
    if secret != lb.settings.webhook_secret:
        raise HTTPException(status_code=401, detail="invalid webhook secret")

    body: dict[str, Any] = await request.json()
    update_id = body.get("update_id")
    if update_id is None:
        raise HTTPException(status_code=400, detail="missing update_id")

    if not await claim_telegram_update(lb.session_factory, int(update_id)):
        log.info("duplicate update_id=%s skipped", update_id)
        return Response(status_code=200)

    update = Update.model_validate(body)
    await lb.dp.feed_update(lb.bot, update)
    return Response(status_code=200)
