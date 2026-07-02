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
from app.db import ensure_db_ready
from app.paths import STATIC_DIR
from app.routers import api, cron, dashboard, webhooks
from app.services.reminders import send_daily_reminders_sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialização idempotente para local, Docker e Vercel.

    Em serverless, algumas invocações podem ocorrer em cold starts diferentes.
    Por isso o banco da demo também é garantido em `get_db()` e no `/health`.
    """
    global scheduler
    ensure_db_ready(seed=True)

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


app = FastAPI(title=settings.app_name, version="0.1.1", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(webhooks.router)
app.include_router(cron.router)
app.include_router(api.router)
app.include_router(dashboard.router)


@app.get("/health", include_in_schema=False)
def public_health() -> dict:
    ensure_db_ready(seed=False)
    return {"ok": True, "service": settings.app_name, "env": settings.app_env}
