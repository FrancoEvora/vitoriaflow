from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import verify_meta_signature
from app.db import get_db
from app.models import Interaction
from app.services.vitoria import VitoriaAgent
from app.services.whatsapp import WhatsAppClient, extract_incoming_messages

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("/whatsapp", response_class=PlainTextResponse)
async def verify_whatsapp_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    settings = get_settings()
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        return hub_challenge or ""
    raise HTTPException(status_code=403, detail="Token de verificação inválido")


@router.post("/whatsapp")
async def receive_whatsapp_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    raw_body = await request.body()
    if not verify_meta_signature(settings.whatsapp_app_secret, raw_body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Assinatura inválida")

    payload = await request.json()
    messages = extract_incoming_messages(payload)
    agent = VitoriaAgent()
    whatsapp = WhatsAppClient()

    for item in messages:
        if not item.get("from_phone"):
            continue
        reply = agent.handle_incoming(
            db=db,
            from_phone=item["from_phone"],
            text=item.get("text"),
            profile_name=item.get("profile_name"),
        )
        db.add(
            Interaction(
                lead_id=None,
                broker_id=None,
                direction="outbound",
                channel="whatsapp",
                message=reply,
                summary="Resposta automática da Vitória via webhook.",
            )
        )
        db.commit()
        await whatsapp.send_text(item["from_phone"], reply)

    return {"ok": True, "messages_processed": len(messages)}
