from __future__ import annotations

import secrets

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.core.config import get_settings
from app.services.reminders import send_daily_reminders_sync

router = APIRouter(prefix="/api/cron", tags=["cron"])


@router.get("/daily-reminders")
def daily_reminders(
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict:
    """Dispara lembretes diários da Vitória.

    - Chamadas automáticas do Vercel Cron são aceitas pelos cabeçalhos padrão.
    - Chamadas manuais devem enviar Authorization: Bearer <CRON_SECRET>, quando
      CRON_SECRET estiver configurado.
    """

    settings = get_settings()
    user_agent = request.headers.get("user-agent", "").lower()
    cron_schedule = request.headers.get("x-vercel-cron-schedule")
    is_vercel_cron = "vercel-cron/1.0" in user_agent or bool(cron_schedule)

    if not is_vercel_cron:
        if not settings.cron_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Endpoint reservado para Vercel Cron. Configure CRON_SECRET para chamadas manuais.",
            )
        expected = f"Bearer {settings.cron_secret}"
        if not authorization or not secrets.compare_digest(authorization, expected):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="CRON_SECRET inválido ou ausente.",
            )

    send_daily_reminders_sync()
    return {"ok": True, "message": "Lembretes diários processados pela Vitória."}
