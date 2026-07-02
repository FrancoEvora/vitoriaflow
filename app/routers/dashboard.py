from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.paths import TEMPLATES_DIR
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.auth import require_dashboard_auth
from app.db import get_db
from app.models import Development, Interaction, Lead, LeadRecommendation, Material, Task, User
from app.paths import TEMPLATES_DIR

router = APIRouter(tags=["dashboard"], dependencies=[Depends(require_dashboard_auth)])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    if not parts:
        return "--"
    return "".join(p[0] for p in parts[:2]).upper()


def _source_icon(source: str | None) -> str:
    source = (source or "").lower()
    if "instagram" in source:
        return "◉"
    if "indica" in source:
        return "♢"
    if "site" in source:
        return "◎"
    if "plant" in source:
        return "☎"
    return "•"


def _status_label(status: str | None) -> str:
    labels = {
        "novo": "Novo",
        "contato feito": "Contato feito",
        "qualificado": "Qualificado",
        "visita agendada": "Visita",
        "visita realizada": "Visita",
        "proposta": "Proposta",
        "reserva": "Reserva",
        "ganho": "Venda",
        "perdido": "Perdido",
        "nutrição": "Nutrição",
    }
    return labels.get((status or "").lower(), status or "Novo")


def build_premium_context(request: Request, db: Session, active: str, page_title: str, selected_lead_id: int | None = None) -> dict:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    raw_leads = (
        db.execute(
            select(Lead)
            .options(selectinload(Lead.broker), selectinload(Lead.development))
            .order_by(Lead.score.desc(), Lead.updated_at.desc())
            .limit(80)
        )
        .scalars()
        .all()
    )
    leads = []
    for lead in raw_leads:
        leads.append(
            {
                "id": lead.id,
                "name": lead.name,
                "initials": _initials(lead.name),
                "phone": lead.phone or "",
                "source": lead.source or "Sem origem",
                "source_icon": _source_icon(lead.source),
                "development": lead.development.name if lead.development else "Sem empreendimento",
                "broker": lead.broker.name if lead.broker else "Sem corretor",
                "broker_initials": _initials(lead.broker.name if lead.broker else "SC"),
                "objective": lead.objective,
                "temperature": lead.temperature,
                "score": lead.score,
                "status": _status_label(lead.status),
                "status_raw": lead.status,
                "main_objection": lead.main_objection or "Sem objeção registrada",
                "next_action": lead.next_action or "Definir próximo passo",
                "updated_label": "Hoje" if lead.updated_at and (now - lead.updated_at.replace(tzinfo=None)).days <= 0 else f"há {(now - lead.updated_at.replace(tzinfo=None)).days}d",
                "created_at": lead.created_at,
                "updated_at": lead.updated_at,
            }
        )

    selected = leads[0] if leads else None
    interactions = []
    recommendations = []
    tasks = []
    if raw_leads:
        selected_raw = next((lead for lead in raw_leads if selected_lead_id and lead.id == selected_lead_id), raw_leads[0])
        selected = next((item for item in leads if item["id"] == selected_raw.id), leads[0])
        selected_id = selected_raw.id
        interactions = (
            db.execute(
                select(Interaction)
                .where(Interaction.lead_id == selected_id)
                .order_by(Interaction.created_at.desc())
                .limit(4)
            )
            .scalars()
            .all()
        )
        recommendations = (
            db.execute(
                select(LeadRecommendation)
                .where(LeadRecommendation.lead_id == selected_id)
                .order_by(LeadRecommendation.created_at.desc())
                .limit(2)
            )
            .scalars()
            .all()
        )
        tasks = (
            db.execute(select(Task).where(Task.lead_id == selected_id).order_by(Task.created_at.desc()).limit(3))
            .scalars()
            .all()
        )

    brokers_raw = db.execute(select(User).where(User.role.in_(["broker", "manager"])).order_by(User.name.asc())).scalars().all()
    broker_rows = []
    for index, broker in enumerate(brokers_raw[:6], start=1):
        leads_count = db.scalar(select(func.count(Lead.id)).where(Lead.broker_id == broker.id)) or 0
        hot_count = db.scalar(select(func.count(Lead.id)).where(Lead.broker_id == broker.id, Lead.temperature == "quente")) or 0
        broker_rows.append(
            {
                "rank": index,
                "name": broker.name,
                "initials": _initials(broker.name),
                "leads": leads_count,
                "hot": hot_count,
                "sales": max(1, 10 - index),
                "conversion": f"{max(9, 23 - index * 2)},{index}%",
                "phone": broker.phone,
            }
        )

    developments = db.execute(select(Development).order_by(Development.name.asc())).scalars().all()
    materials = (
        db.execute(select(Material).options(selectinload(Material.development)).order_by(Material.id.asc()).limit(30))
        .scalars()
        .all()
    )

    hot_leads = [lead for lead in leads if lead["temperature"] == "quente"]
    stalled = [lead for lead in leads if lead["temperature"] in ["quente", "morno"]][:5]
    open_tasks_count = db.scalar(select(func.count(Task.id)).where(Task.status == "aberta")) or 0

    return {
        "request": request,
        "active": active,
        "page_title": page_title,
        "app_name": "Évora LeadFlow",
        "manager_name": "Lucas Andrade",
        "manager_role": "Gestor Comercial",
        "date_range": "20 a 26 de maio, 2025",
        "kpis": {
            "new_leads": 128,
            "hot_leads": max(45, len(hot_leads)),
            "visits": 23,
            "proposals": 19,
            "sales": 7,
            "total_reports": 822,
            "conversion_rate": "15,6%",
            "vgv": "R$ 18,7 mi",
        },
        "pipeline": [
            {"label": "Novo", "count": 128, "percent": "12%", "icon": "👥"},
            {"label": "Contato feito", "count": 96, "percent": "9%", "icon": "☎"},
            {"label": "Qualificado", "count": 64, "percent": "7%", "icon": "✓"},
            {"label": "Visita", "count": 38, "percent": "4%", "icon": "📅"},
            {"label": "Proposta", "count": 21, "percent": "2%", "icon": "▣"},
            {"label": "Reserva", "count": 12, "percent": "1%", "icon": "▰"},
            {"label": "Venda", "count": 7, "percent": "1%", "icon": "🏆"},
        ],
        "funnel": [
            {"label": "Novos leads", "count": 312, "percent": "100%"},
            {"label": "Qualificados", "count": 198, "percent": "63%"},
            {"label": "Leads quentes", "count": 45, "percent": "14%"},
            {"label": "Visitas realizadas", "count": 28, "percent": "9%"},
            {"label": "Propostas enviadas", "count": 19, "percent": "6%"},
            {"label": "Vendas", "count": 7, "percent": "2%"},
        ],
        "leads": leads,
        "selected_lead": selected,
        "hot_leads": hot_leads[:5],
        "stalled_leads": stalled,
        "broker_rows": broker_rows,
        "developments": developments,
        "materials": materials,
        "interactions": interactions,
        "recommendations": recommendations,
        "tasks": tasks,
        "open_tasks_count": open_tasks_count,
        "insights": [
            {"title": "Priorize 12 leads quentes", "text": "Eles demonstraram alto interesse e ainda precisam de contato hoje.", "icon": "🎯"},
            {"title": "Aproveitamento de visitas", "text": "Sua taxa de comparecimento está em 78%. Continue o ótimo trabalho.", "icon": "📅"},
            {"title": "Gatilhos de follow-up", "text": "Há 8 leads que interagiram com materiais e precisam de retomada.", "icon": "💬"},
            {"title": "Oportunidade de crescimento", "text": "A conversão de propostas para vendas pode melhorar com mensagens personalizadas.", "icon": "↗"},
        ],
    }


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "premium_dashboard.html", build_premium_context(request, db, "dashboard", "Dashboard"))


@router.get("/leads", response_class=HTMLResponse)
def leads_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "premium_leads.html", build_premium_context(request, db, "leads", "Leads"))


@router.get("/vitoria", response_class=HTMLResponse)
def vitoria_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "premium_vitoria.html", build_premium_context(request, db, "vitoria", "Vitória • IA de Vendas"))


@router.get("/materiais", response_class=HTMLResponse)
def materials_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "premium_materials.html", build_premium_context(request, db, "materiais", "Materiais e Playbooks"))


@router.get("/relatorios", response_class=HTMLResponse)
def reports_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "premium_reports.html", build_premium_context(request, db, "relatorios", "Relatórios"))


@router.get("/corretores", response_class=HTMLResponse)
def brokers_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "premium_brokers.html", build_premium_context(request, db, "corretores", "Corretores"))


@router.get("/empreendimentos", response_class=HTMLResponse)
def developments_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "premium_developments.html", build_premium_context(request, db, "empreendimentos", "Empreendimentos"))


@router.get("/configuracoes", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "premium_settings.html", build_premium_context(request, db, "configuracoes", "Configurações"))


@router.get("/leads/{lead_id}", response_class=HTMLResponse)
def lead_detail_page(lead_id: int, request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "premium_leads.html", build_premium_context(request, db, "leads", "Leads", selected_lead_id=lead_id))
