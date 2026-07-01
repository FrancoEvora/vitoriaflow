from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ScoreResult:
    score: int
    temperature: str
    next_action: str


def _norm(value: str | None) -> str:
    return (value or "").strip().lower()


def _has_money(value: str | None) -> bool:
    text = _norm(value)
    return bool(re.search(r"\d", text)) or any(word in text for word in ["mil", "entrada", "parcela", "financia"])


def score_lead(payload: dict) -> ScoreResult:
    """Score inicial simples, combinando intenção, prazo, orçamento, visita e objeção."""

    score = 0
    objective = _norm(payload.get("objective"))
    timeline = _norm(payload.get("purchase_timeline"))
    entry = payload.get("budget_entry")
    installment = payload.get("budget_installment")
    objection = _norm(payload.get("main_objection"))
    source = _norm(payload.get("source"))
    knows = bool(payload.get("knows_development"))

    if any(x in objective for x in ["invest", "mor", "constru", "casa", "filho"]):
        score += 15
    if any(x in timeline for x in ["agora", "hoje", "essa semana", "este mês", "esse mês", "30", "mês"]):
        score += 25
    elif any(x in timeline for x in ["60", "90", "3 meses", "trimestre"]):
        score += 15
    elif any(x in timeline for x in ["ano", "futuro", "sem pressa"]):
        score += 5

    if _has_money(entry):
        score += 15
    if _has_money(installment):
        score += 10
    if knows:
        score += 10
    if any(x in source for x in ["indicação", "indicacao", "cliente", "amigo"]):
        score += 10
    if objection and objection not in ["não", "nao", "nenhuma", "sem objeção", "sem objecao"]:
        score += 5
    if any(x in objection for x in ["sumiu", "não responde", "nao responde", "sem resposta"]):
        score -= 15
    if "só tabela" in objection or "so tabela" in objection:
        score -= 10

    score = max(0, min(100, score))
    if score >= 75:
        temperature = "quente"
    elif score >= 50:
        temperature = "morno"
    else:
        temperature = "frio"

    next_action = recommend_next_action(payload, temperature)
    return ScoreResult(score=score, temperature=temperature, next_action=next_action)


def recommend_next_action(payload: dict, temperature: str) -> str:
    objective = _norm(payload.get("objective"))
    objection = _norm(payload.get("main_objection"))
    knows = bool(payload.get("knows_development"))

    if "entrada" in objection or "parcela" in objection or "caro" in objection:
        return "Gerar simulação alternativa e conduzir para visita antes de negociar desconto."
    if "document" in objection or "seguran" in objection or "medo" in objection:
        return "Enviar prova de segurança: documentação, histórico da loteadora e fotos de obra."
    if "invest" in objective:
        return "Enviar mapa de localização, argumento de valorização e selecionar lotes com maior liquidez."
    if "constru" in objective or "mor" in objective:
        if knows:
            return "Reforçar plano de construção e agendar visita para escolha de quadra."
        return "Enviar vídeo do empreendimento, mapa de localização e convidar para visita."
    if temperature == "quente":
        return "Agendar visita ou chamada de proposta ainda hoje."
    if temperature == "morno":
        return "Qualificar motivação principal e enviar material de apresentação."
    return "Fazer pergunta de diagnóstico antes de enviar tabela."
