from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Lead, Task, User
from app.services.whatsapp import WhatsAppClient

logger = logging.getLogger(__name__)


def build_broker_daily_summary(db: Session, broker: User) -> str | None:
    active_leads = db.execute(
        select(Lead).where(Lead.broker_id == broker.id, Lead.status.notin_(["ganho", "perdido"]))
    ).scalars().all()
    if not active_leads:
        return None

    now = datetime.now(timezone.utc)
    stalled = [lead for lead in active_leads if lead.updated_at and lead.updated_at <= now - timedelta(hours=48)]
    hot = [lead for lead in active_leads if lead.temperature == "quente"]
    due_tasks = db.execute(
        select(Task).where(Task.broker_id == broker.id, Task.status == "aberta", Task.due_at <= now)
    ).scalars().all()

    lines = [f"Bom dia, {broker.name}. Aqui é a Vitória. Vamos organizar sua carteira?"]
    lines.append("")
    lines.append(f"Leads ativos: {len(active_leads)}")
    lines.append(f"Leads quentes: {len(hot)}")
    lines.append(f"Leads sem atualização há 48h+: {len(stalled)}")
    lines.append(f"Tarefas vencidas: {len(due_tasks)}")

    priority = hot[:3] or stalled[:3]
    if priority:
        lines.append("")
        lines.append("Prioridades de hoje:")
        for lead in priority:
            lines.append(f"• {lead.name}: {lead.next_action or 'definir próximo passo'}")

    lines.append("")
    lines.append("Responda 'Meus leads' ou 'Leads parados' para revisar comigo.")
    return "\n".join(lines)[:4096]


async def send_daily_reminders() -> None:
    whatsapp = WhatsAppClient()
    with SessionLocal() as db:
        brokers = db.execute(select(User).where(User.role == "broker", User.active.is_(True))).scalars().all()
        for broker in brokers:
            body = build_broker_daily_summary(db, broker)
            if body:
                try:
                    await whatsapp.send_text(broker.phone, body)
                except Exception as exc:  # pragma: no cover - depende da API externa
                    logger.exception("Falha ao enviar lembrete para %s: %s", broker.phone, exc)


def send_daily_reminders_sync() -> None:
    asyncio.run(send_daily_reminders())
