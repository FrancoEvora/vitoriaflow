from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from zoneinfo import ZoneInfo

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
except Exception:  # pragma: no cover - demo still runs without the optional local scheduler
    AsyncIOScheduler = None  # type: ignore
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.db import SessionLocal, init_db
from app.routers import api, cron, dashboard, webhooks
from app.seed_data import seed_if_empty
from app.services.reminders import send_daily_reminders_sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    init_db()
    with SessionLocal() as db:
        seed_if_empty(db)

    running_on_vercel = os.getenv("VERCEL") == "1" or settings.app_env.lower() == "vercel"
    if settings.enable_scheduler and not running_on_vercel and AsyncIOScheduler is not None:
        scheduler = AsyncIOScheduler(timezone=ZoneInfo(settings.timezone))
        scheduler.add_job(
            send_daily_reminders_sync,
            "cron",
            hour=settings.daily_reminder_hour,
            minute=0,
            id="daily_broker_reminders",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Scheduler de lembretes iniciado para %s:00", settings.daily_reminder_hour)
    elif running_on_vercel:
        logger.info("Scheduler local desativado na Vercel; use Vercel Cron em /api/cron/daily-reminders.")

    yield

    if scheduler:
        scheduler.shutdown(wait=False)


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(webhooks.router)
app.include_router(cron.router)
app.include_router(api.router)
app.include_router(dashboard.router)


@app.get("/health", include_in_schema=False)
def public_health() -> dict:
    return {"ok": True, "service": settings.app_name, "env": settings.app_env}
