from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import (
    ConversationSession,
    Development,
    Interaction,
    Lead,
    LeadRecommendation,
    Task,
    User,
)
from app.services.ai import generate_objection_script, generate_recommendation
from app.services.scoring import score_lead

NEW_LEAD_TRIGGERS = [
    "tenho um lead",
    "novo lead",
    "cadastrar lead",
    "cadastra um lead",
    "cadastre um lead",
    "lead novo",
]

FLOW_STEPS = [
    ("name", "Qual é o nome do lead?"),
    ("phone", "Qual é o telefone do lead? Se não tiver agora, responda 'não tenho'."),
    ("source", "Esse lead veio de qual origem? Instagram, indicação, plantão, tráfego pago, placa ou outro canal?"),
    ("development_name", "Qual empreendimento ele está avaliando?"),
    ("objective", "Ele quer lote para morar, construir no futuro ou investir?"),
    ("budget", "Ele já falou sobre entrada, parcela ou faixa de investimento?"),
    ("purchase_timeline", "Prazo de decisão: agora, 30 dias, 90 dias ou mais?"),
    ("knows_development", "Ele já conhece o empreendimento? Responda sim ou não."),
    ("main_objection", "Qual é a principal dúvida ou objeção até agora? Se não tiver, responda 'nenhuma'."),
]


def normalize_phone(phone: str | None) -> str:
    if not phone:
        return ""
    return re.sub(r"\D", "", phone)


def compact(text: str | None) -> str:
    return (text or "").strip()


def lower(text: str | None) -> str:
    return compact(text).lower()


def parse_budget(text: str) -> tuple[str | None, str | None]:
    normalized = lower(text)
    entry = None
    installment = None

    entry_match = re.search(r"entrada[^\d]*(R\$\s*)?([\d\.,]+\s*(mil)?)", normalized)
    installment_match = re.search(r"parcela[^\d]*(R\$\s*)?([\d\.,]+\s*(mil)?)", normalized)
    generic_values = re.findall(r"(R\$\s*)?\d+[\d\.,]*(\s*mil)?", text, flags=re.IGNORECASE)

    if entry_match:
        entry = entry_match.group(2)
    if installment_match:
        installment = installment_match.group(2)

    if not entry and "entrada" in normalized:
        entry = text
    if not installment and "parcela" in normalized:
        installment = text
    if not entry and not installment and generic_values:
        entry = text

    return entry, installment


def parse_objective(text: str) -> str:
    value = lower(text)
    if "invest" in value:
        return "investimento"
    if "constru" in value:
        return "construção futura"
    if "mor" in value or "casa" in value:
        return "moradia"
    return compact(text) or "indefinido"


def parse_yes_no(text: str) -> bool:
    value = lower(text)
    return any(word in value for word in ["sim", "conhece", "visitou", "já", "ja"])


class VitoriaAgent:
    """Orquestrador conversacional da Vitória."""

    def handle_incoming(
        self,
        db: Session,
        from_phone: str,
        text: str | None,
        profile_name: str | None = None,
    ) -> str:
        phone = normalize_phone(from_phone)
        message = compact(text)
        broker = self._get_or_create_broker(db, phone, profile_name)
        self._log_interaction(db, broker.id, None, "inbound", message or "[mensagem sem texto]")

        if not message:
            return "Recebi sua mensagem, mas ainda não consegui interpretar mídia/áudio neste MVP. Me envie em texto: 'Tenho um lead' ou 'Meus leads'."

        session = self._get_session(db, broker)
        if session and session.topic == "new_lead" and session.state != "idle":
            return self._continue_new_lead_flow(db, broker, session, message)

        msg = lower(message)
        if any(trigger in msg for trigger in NEW_LEAD_TRIGGERS):
            return self._start_new_lead_flow(db, broker)

        if "meus leads" in msg or "minha carteira" in msg or "pipeline" in msg:
            return self._broker_pipeline(db, broker)

        if "parado" in msg or "atrasado" in msg or "follow" in msg:
            return self._stalled_leads(db, broker)

        if msg.startswith("atualiza") or msg.startswith("atualizar") or msg.startswith("update"):
            return self._update_lead_from_free_text(db, broker, message)

        if "script" in msg or "objeção" in msg or "objecao" in msg or "achou caro" in msg:
            return self._script_reply(message)

        if "ajuda" in msg or "menu" in msg or "vitória" in msg or "vitoria" in msg:
            return self._help()

        return (
            "Sou a Vitória, agente comercial do Évora LeadFlow.\n\n"
            "Posso te ajudar com:\n"
            "• 'Tenho um lead'\n"
            "• 'Meus leads'\n"
            "• 'Leads parados'\n"
            "• 'Atualiza Mariana: pediu simulação'\n"
            "• 'Script para objeção de entrada'"
        )

    def _get_or_create_broker(self, db: Session, phone: str, profile_name: str | None) -> User:
        broker = db.execute(select(User).where(User.phone == phone)).scalar_one_or_none()
        if broker:
            return broker
        broker = User(name=profile_name or f"Corretor {phone[-4:]}", phone=phone, role="broker", active=True)
        db.add(broker)
        db.commit()
        db.refresh(broker)
        return broker

    def _get_session(self, db: Session, broker: User) -> ConversationSession | None:
        return db.execute(
            select(ConversationSession).where(ConversationSession.broker_id == broker.id).order_by(ConversationSession.id.desc())
        ).scalar_one_or_none()

    def _start_new_lead_flow(self, db: Session, broker: User) -> str:
        session = self._get_session(db, broker)
        if not session:
            session = ConversationSession(broker_id=broker.id, phone=broker.phone, topic="new_lead", state="name", payload={})
            db.add(session)
        else:
            session.topic = "new_lead"
            session.state = "name"
            session.payload = {}
        db.commit()
        return "Perfeito. Vamos cadastrar esse lead.\n\nQual é o nome do lead?"

    def _continue_new_lead_flow(self, db: Session, broker: User, session: ConversationSession, message: str) -> str:
        payload: dict[str, Any] = dict(session.payload or {})
        current_state = session.state

        if current_state == "budget":
            entry, installment = parse_budget(message)
            payload["budget_entry"] = entry
            payload["budget_installment"] = installment
        elif current_state == "objective":
            payload["objective"] = parse_objective(message)
        elif current_state == "knows_development":
            payload["knows_development"] = parse_yes_no(message)
        else:
            payload[current_state] = compact(message)

        current_index = [step[0] for step in FLOW_STEPS].index(current_state)
        if current_index + 1 >= len(FLOW_STEPS):
            session.payload = payload
            session.state = "idle"
            session.topic = "idle"
            db.commit()
            return self._finalize_new_lead(db, broker, payload)

        next_state, question = FLOW_STEPS[current_index + 1]
        session.payload = payload
        session.state = next_state
        db.commit()
        return question

    def _finalize_new_lead(self, db: Session, broker: User, payload: dict[str, Any]) -> str:
        development = self._find_or_create_development(db, payload.get("development_name"))
        score_result = score_lead(payload)

        lead = Lead(
            name=payload.get("name") or "Lead sem nome",
            phone=None if lower(payload.get("phone")) in ["não tenho", "nao tenho", "não", "nao"] else payload.get("phone"),
            source=payload.get("source"),
            development_id=development.id if development else None,
            broker_id=broker.id,
            objective=payload.get("objective") or "indefinido",
            budget_entry=payload.get("budget_entry"),
            budget_installment=payload.get("budget_installment"),
            purchase_timeline=payload.get("purchase_timeline"),
            knows_development=bool(payload.get("knows_development")),
            main_objection=payload.get("main_objection"),
            score=score_result.score,
            temperature=score_result.temperature,
            next_action=score_result.next_action,
            status="qualificado" if score_result.score >= 50 else "novo",
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

        lead_payload = self._lead_to_payload(lead, development)
        recommendation = generate_recommendation(lead_payload, self._development_to_payload(development))
        db.add(
            LeadRecommendation(
                lead_id=lead.id,
                diagnosis=recommendation["diagnosis"],
                strategy=recommendation["strategy"],
                script=recommendation["script"],
                materials=recommendation.get("materials", []),
            )
        )
        db.add(
            Task(
                lead_id=lead.id,
                broker_id=broker.id,
                task_type="follow_up",
                description=score_result.next_action,
                due_at=datetime.now(timezone.utc) + timedelta(days=1),
                status="aberta",
            )
        )
        self._log_interaction(db, broker.id, lead.id, "system", "Lead cadastrado pela Vitória.")
        db.commit()

        reply = (
            f"Lead cadastrado.\n\n"
            f"*Lead:* {lead.name}\n"
            f"*Perfil:* {lead.objective}\n"
            f"*Temperatura:* {lead.temperature}\n"
            f"*Score:* {lead.score}/100\n"
            f"*Próxima ação:* {lead.next_action}\n\n"
            f"*Diagnóstico:* {recommendation['diagnosis']}\n\n"
            f"*Estratégia:* {recommendation['strategy']}\n\n"
            f"*Mensagem sugerida:*\n{recommendation['script']}"
        )
        return reply[:4096]

    def _find_or_create_development(self, db: Session, name: str | None) -> Development | None:
        clean = compact(name)
        if not clean or lower(clean) in ["não sei", "nao sei", "indefinido", "nenhum"]:
            return db.execute(select(Development).order_by(Development.id.asc())).scalars().first()

        existing = db.execute(select(Development).where(Development.name == clean)).scalars().first()
        if not existing:
            existing = db.execute(
                select(Development).where(func.lower(Development.name).contains(lower(clean)))
            ).scalars().first()
        if existing:
            return existing

        development = Development(name=clean, city=None, status="ativo", description="Criado automaticamente pela Vitória.")
        db.add(development)
        try:
            db.commit()
        except Exception:
            db.rollback()
            return db.execute(select(Development).where(Development.name == clean)).scalars().first()
        db.refresh(development)
        return development

    def _broker_pipeline(self, db: Session, broker: User) -> str:
        leads = db.execute(
            select(Lead).where(Lead.broker_id == broker.id, Lead.status.notin_(["ganho", "perdido"])).order_by(Lead.updated_at.desc()).limit(10)
        ).scalars().all()
        if not leads:
            return "Você ainda não tem leads ativos cadastrados. Para começar, me envie: 'Tenho um lead'."

        lines = ["Sua carteira ativa:"]
        for lead in leads:
            lines.append(f"• {lead.name} — {lead.temperature}, status {lead.status}. Próxima ação: {lead.next_action or 'definir próximo passo'}")
        return "\n".join(lines)[:4096]

    def _stalled_leads(self, db: Session, broker: User) -> str:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
        leads = db.execute(
            select(Lead)
            .where(
                Lead.broker_id == broker.id,
                Lead.status.notin_(["ganho", "perdido"]),
                or_(Lead.updated_at <= cutoff, Lead.temperature == "quente"),
            )
            .order_by(Lead.temperature.desc(), Lead.updated_at.asc())
            .limit(10)
        ).scalars().all()
        if not leads:
            return "Boa. Não encontrei leads críticos parados na sua carteira agora."

        lines = ["Leads que precisam de atenção:"]
        for lead in leads:
            lines.append(f"• {lead.name} — {lead.temperature}. Ação sugerida: {lead.next_action or 'retomar contato'}")
        lines.append("\nResponda: 'Atualiza NOME: ...' para registrar avanço.")
        return "\n".join(lines)[:4096]

    def _update_lead_from_free_text(self, db: Session, broker: User, message: str) -> str:
        match = re.match(r"atualiz[ae]?\s+([^:,-]+)[:,-]?\s*(.*)", message, flags=re.IGNORECASE)
        if not match:
            return "Me envie assim: 'Atualiza Mariana: pediu simulação e quer visitar sábado'."

        lead_name = compact(match.group(1))
        note = compact(match.group(2)) or message
        lead = db.execute(
            select(Lead)
            .where(Lead.broker_id == broker.id, func.lower(Lead.name).contains(lower(lead_name)))
            .order_by(Lead.updated_at.desc())
        ).scalars().first()
        if not lead:
            return f"Não encontrei um lead chamado {lead_name} na sua carteira. Você pode cadastrar com: 'Tenho um lead'."

        msg = lower(note)
        if "visit" in msg:
            lead.status = "visita realizada" if any(x in msg for x in ["foi", "realizada", "visitou"]) else "visita agendada"
        if "simula" in msg or "proposta" in msg:
            lead.status = "proposta"
        if "comprou" in msg or "fechou" in msg or "contrato" in msg:
            lead.status = "ganho"
        if "perdeu" in msg or "desistiu" in msg:
            lead.status = "perdido"
        if "caro" in msg:
            lead.main_objection = "Preço percebido como alto"
        if "entrada" in msg:
            lead.main_objection = "Entrada"
        if "sumiu" in msg or "sem resposta" in msg:
            lead.main_objection = "Sem resposta"

        payload = self._lead_to_payload(lead, lead.development)
        payload["main_objection"] = lead.main_objection
        score_result = score_lead(payload)
        lead.score = score_result.score
        lead.temperature = score_result.temperature
        lead.next_action = score_result.next_action
        lead.updated_at = datetime.now(timezone.utc)
        self._log_interaction(db, broker.id, lead.id, "inbound", note)
        db.add(
            Task(
                lead_id=lead.id,
                broker_id=broker.id,
                task_type="follow_up",
                description=score_result.next_action,
                due_at=datetime.now(timezone.utc) + timedelta(days=1),
                status="aberta",
            )
        )
        db.commit()

        script = generate_objection_script(lead.main_objection or note, lead.objective, lead.name)
        return (
            f"Atualizado.\n\n"
            f"*Lead:* {lead.name}\n"
            f"*Status:* {lead.status}\n"
            f"*Temperatura:* {lead.temperature}\n"
            f"*Próxima ação:* {lead.next_action}\n\n"
            f"*Mensagem sugerida:*\n{script}"
        )[:4096]

    def _script_reply(self, message: str) -> str:
        script = generate_objection_script(message)
        return f"Aqui vai um script direto:\n\n{script}"

    def _help(self) -> str:
        return (
            "Sou a Vitória. Posso cadastrar leads, orientar abordagem e cobrar follow-up.\n\n"
            "Comandos úteis:\n"
            "• Tenho um lead\n"
            "• Meus leads\n"
            "• Leads parados\n"
            "• Atualiza Mariana: pediu entrada menor\n"
            "• Script para objeção de preço"
        )

    def _lead_to_payload(self, lead: Lead, development: Development | None) -> dict[str, Any]:
        return {
            "id": lead.id,
            "name": lead.name,
            "phone": lead.phone,
            "source": lead.source,
            "development": development.name if development else None,
            "objective": lead.objective,
            "budget_entry": lead.budget_entry,
            "budget_installment": lead.budget_installment,
            "purchase_timeline": lead.purchase_timeline,
            "knows_development": lead.knows_development,
            "temperature": lead.temperature,
            "score": lead.score,
            "status": lead.status,
            "main_objection": lead.main_objection,
            "next_action": lead.next_action,
        }

    def _development_to_payload(self, development: Development | None) -> dict[str, Any] | None:
        if not development:
            return None
        return {
            "id": development.id,
            "name": development.name,
            "city": development.city,
            "status": development.status,
            "description": development.description,
            "sales_arguments": development.sales_arguments,
        }

    def _log_interaction(self, db: Session, broker_id: int | None, lead_id: int | None, direction: str, message: str) -> None:
        db.add(
            Interaction(
                broker_id=broker_id,
                lead_id=lead_id,
                direction=direction,
                channel="whatsapp",
                message=message,
            )
        )
        db.commit()
