from __future__ import annotations

import json
import logging
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)

VITORIA_SYSTEM_PROMPT = """
Você é Vitória, a agente comercial inteligente do Évora LeadFlow.
Sua função é ajudar corretores de loteamentos a cadastrar leads, qualificar oportunidades, recomendar estratégias de venda, gerar scripts de abordagem, lembrar follow-ups e manter o funil comercial atualizado.
Fale em português do Brasil, de forma objetiva, consultiva e firme.
Seu foco é sempre fazer o lead avançar para o próximo passo comercial.
Você atua como uma coordenadora comercial digital, não como uma atendente genérica.
Sempre identifique intenção de compra, temperatura, objeção principal, próxima ação e mensagem sugerida.
Nunca deixe um lead sem próximo passo.
""".strip()

RECOMMENDATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "diagnosis": {"type": "string"},
        "strategy": {"type": "string"},
        "script": {"type": "string"},
        "materials": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["diagnosis", "strategy", "script", "materials"],
}


def _norm(value: str | None) -> str:
    return (value or "").lower()


def fallback_recommendation(lead_payload: dict, development: dict | None = None) -> dict[str, Any]:
    """Estratégia determinística para rodar o MVP mesmo sem OPENAI_API_KEY."""

    objective = _norm(lead_payload.get("objective"))
    objection = _norm(lead_payload.get("main_objection"))
    name = lead_payload.get("name") or "o lead"

    materials = ["Vídeo aéreo do empreendimento", "Mapa de localização"]

    if "invest" in objective:
        diagnosis = f"{name} tem perfil de investidor. A venda deve enfatizar localização, fase da região, escassez e liquidez futura."
        strategy = "Não comece pelo sonho da casa. Mostre lógica de investimento, potencial de valorização e escolha de lote com boa liquidez."
        script = (
            f"{name}, olhando pelo lado de investimento, o ponto principal é entender localização, potencial de valorização "
            "e momento de entrada. Vou te mandar um material rápido da região e depois te mostro quais lotes fazem mais sentido para esse perfil."
        )
        materials.extend(["Argumentos de valorização", "Quadras com maior liquidez"])
    elif "entrada" in objection or "parcela" in objection or "caro" in objection:
        diagnosis = f"{name} demonstra interesse, mas a barreira principal é financeira. Ainda não é uma perda; é ajuste de condição."
        strategy = "Evite partir direto para desconto. Gere nova simulação, compare opções de quadra e tente agendar visita."
        script = (
            f"{name}, consigo verificar uma condição mais leve para você. Antes disso, queria te mostrar duas opções de lote, "
            "porque a escolha da quadra pode influenciar bastante a condição. Você consegue visitar comigo esta semana?"
        )
        materials.extend(["Simulação financeira", "Tabela comentada pelo corretor"])
    elif "document" in objection or "seguran" in objection or "medo" in objection:
        diagnosis = f"{name} precisa de confiança. O avanço depende de reduzir risco percebido."
        strategy = "Use histórico da loteadora, documentação, fotos de obra e prova social antes de falar em fechamento."
        script = (
            f"{name}, sua preocupação faz sentido. Antes de falar em proposta, vou te mandar os pontos que dão segurança ao empreendimento: "
            "documentação, infraestrutura e histórico da loteadora. Depois olhamos a melhor opção com calma."
        )
        materials.extend(["FAQ documental", "Fotos de obra", "Depoimentos de compradores"])
    else:
        diagnosis = f"{name} precisa ser qualificado antes de receber tabela. A prioridade é entender motivação e prazo."
        strategy = "Faça uma pergunta consultiva, identifique moradia/construção/investimento e só depois envie materiais."
        script = (
            f"{name}, antes de te mandar valores, quero entender rapidinho: você está olhando esse lote mais para morar, "
            "construir no futuro ou investir? Assim te mostro as opções que fazem mais sentido."
        )

    return {
        "diagnosis": diagnosis,
        "strategy": strategy,
        "script": script,
        "materials": materials,
    }


def generate_recommendation(lead_payload: dict, development: dict | None = None) -> dict[str, Any]:
    settings = get_settings()
    if not settings.openai_api_key:
        return fallback_recommendation(lead_payload, development)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        prompt = {
            "lead": lead_payload,
            "development": development or {},
            "contexto": "Venda de loteamento pela Évora Urbanismo. Gere recomendação curta para WhatsApp do corretor.",
        }
        response = client.responses.create(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": VITORIA_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "sales_recommendation",
                    "schema": RECOMMENDATION_SCHEMA,
                    "strict": True,
                }
            },
        )
        raw = response.output_text
        return json.loads(raw)
    except Exception as exc:  # pragma: no cover - depende da API externa
        logger.warning("Falha ao chamar OpenAI. Usando fallback local. Erro: %s", exc)
        return fallback_recommendation(lead_payload, development)


def generate_objection_script(objection: str, objective: str | None = None, lead_name: str | None = None) -> str:
    payload = {
        "name": lead_name or "o cliente",
        "objective": objective or "indefinido",
        "main_objection": objection,
    }
    rec = fallback_recommendation(payload)
    return rec["script"]
