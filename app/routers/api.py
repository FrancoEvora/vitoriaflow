from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import require_dashboard_auth
from app.db import get_db
from app.models import Lead, LeadRecommendation, Task, User
from app.schemas import BrokerOut, LeadOut, SimulateMessageIn, SimulateMessageOut
from app.services.vitoria import VitoriaAgent
from app.core.config import get_settings
from app.paths import STATIC_DIR, TEMPLATES_DIR

router = APIRouter(prefix="/api", tags=["api"], dependencies=[Depends(require_dashboard_auth)])


@router.get("/health")
def health() -> dict:
    return {"ok": True, "service": "evora-leadflow"}


@router.get("/debug/startup")
def debug_startup() -> dict:
    settings = get_settings()
    db_url = settings.database_url or ""
    safe_db = db_url.split(":", 1)[0] + "://..." if ":" in db_url else "not-set"
    return {
        "ok": True,
        "python": sys.version.split()[0],
        "cwd": str(Path.cwd()),
        "vercel": os.getenv("VERCEL"),
        "app_env": settings.app_env,
        "database_url_scheme": safe_db,
        "static_dir_exists": STATIC_DIR.exists(),
        "templates_dir_exists": TEMPLATES_DIR.exists(),
    }


@router.get("/leads", response_model=list[LeadOut])
def list_leads(db: Session = Depends(get_db)):
    return db.execute(select(Lead).order_by(Lead.updated_at.desc()).limit(200)).scalars().all()


@router.get("/leads/{lead_id}")
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    recommendations = db.execute(
        select(LeadRecommendation).where(LeadRecommendation.lead_id == lead_id).order_by(LeadRecommendation.created_at.desc())
    ).scalars().all()
    tasks = db.execute(select(Task).where(Task.lead_id == lead_id).order_by(Task.created_at.desc())).scalars().all()
    return {
        "lead": LeadOut.model_validate(lead),
        "recommendations": [
            {
                "diagnosis": rec.diagnosis,
                "strategy": rec.strategy,
                "script": rec.script,
                "materials": rec.materials,
                "created_at": rec.created_at,
            }
            for rec in recommendations
        ],
        "tasks": [
            {
                "id": task.id,
                "description": task.description,
                "status": task.status,
                "due_at": task.due_at,
            }
            for task in tasks
        ],
    }


@router.get("/brokers", response_model=list[BrokerOut])
def list_brokers(db: Session = Depends(get_db)):
    return db.execute(select(User).where(User.role == "broker").order_by(User.name.asc())).scalars().all()


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)) -> dict:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=48)

    total_leads = db.scalar(select(func.count(Lead.id))) or 0
    hot_leads = db.scalar(select(func.count(Lead.id)).where(Lead.temperature == "quente")) or 0
    active_leads = db.scalar(select(func.count(Lead.id)).where(Lead.status.notin_(["ganho", "perdido"]))) or 0
    stalled_leads = db.scalar(
        select(func.count(Lead.id)).where(Lead.status.notin_(["ganho", "perdido"]), Lead.updated_at <= cutoff)
    ) or 0
    open_tasks = db.scalar(select(func.count(Task.id)).where(Task.status == "aberta")) or 0
    won_leads = db.scalar(select(func.count(Lead.id)).where(Lead.status == "ganho")) or 0

    by_status = db.execute(select(Lead.status, func.count(Lead.id)).group_by(Lead.status)).all()
    by_source = db.execute(select(Lead.source, func.count(Lead.id)).group_by(Lead.source)).all()
    broker_ranking = db.execute(
        select(User.name, func.count(Lead.id)).join(Lead, Lead.broker_id == User.id, isouter=True).where(User.role == "broker").group_by(User.name).order_by(func.count(Lead.id).desc())
    ).all()

    return {
        "total_leads": total_leads,
        "active_leads": active_leads,
        "hot_leads": hot_leads,
        "stalled_leads": stalled_leads,
        "open_tasks": open_tasks,
        "won_leads": won_leads,
        "by_status": [{"status": status or "sem status", "count": count} for status, count in by_status],
        "by_source": [{"source": source or "sem origem", "count": count} for source, count in by_source],
        "broker_ranking": [{"broker": name, "leads": count} for name, count in broker_ranking],
    }


@router.post("/simulate-message", response_model=SimulateMessageOut)
def simulate_message(payload: SimulateMessageIn, db: Session = Depends(get_db)):
    agent = VitoriaAgent()
    reply = agent.handle_incoming(db, payload.from_phone, payload.text, payload.profile_name)
    return SimulateMessageOut(reply=reply)
