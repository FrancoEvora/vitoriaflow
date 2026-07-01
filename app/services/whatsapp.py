from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """Cliente mínimo para WhatsApp Cloud API.

    Em ambiente local, se WHATSAPP_ACCESS_TOKEN ou WHATSAPP_PHONE_NUMBER_ID estiverem vazios,
    o envio fica em modo dry-run e apenas registra a mensagem no log.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.whatsapp_access_token and self.settings.whatsapp_phone_number_id)

    @property
    def base_url(self) -> str:
        return (
            f"https://graph.facebook.com/{self.settings.whatsapp_graph_version}/"
            f"{self.settings.whatsapp_phone_number_id}/messages"
        )

    async def send_text(self, to_phone: str, body: str) -> dict[str, Any]:
        if not self.configured:
            logger.info("[DRY-RUN WhatsApp] Para %s: %s", to_phone, body)
            return {"dry_run": True, "to": to_phone, "body": body}

        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "text",
            "text": {"preview_url": False, "body": body[:4096]},
        }
        headers = {
            "Authorization": f"Bearer {self.settings.whatsapp_access_token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def send_template(
        self,
        to_phone: str,
        template_name: str,
        language_code: str = "pt_BR",
        body_parameters: list[str] | None = None,
    ) -> dict[str, Any]:
        if not self.configured:
            logger.info(
                "[DRY-RUN WhatsApp Template] Para %s template=%s params=%s",
                to_phone,
                template_name,
                body_parameters,
            )
            return {"dry_run": True, "to": to_phone, "template": template_name}

        components = []
        if body_parameters:
            components.append(
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": value} for value in body_parameters],
                }
            )

        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": components,
            },
        }
        headers = {
            "Authorization": f"Bearer {self.settings.whatsapp_access_token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()


def extract_incoming_messages(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Extrai mensagens recebidas do webhook de WhatsApp.

    Retorna itens com: from_phone, message_id, type, text, profile_name.
    Status de entrega/leitura são ignorados nesta versão.
    """

    messages: list[dict[str, Any]] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            contacts = value.get("contacts", []) or []
            contact = contacts[0] if contacts else {}
            profile_name = (contact.get("profile") or {}).get("name")
            for message in value.get("messages", []) or []:
                message_type = message.get("type")
                text = None
                if message_type == "text":
                    text = (message.get("text") or {}).get("body")
                elif message_type == "button":
                    text = (message.get("button") or {}).get("text")
                elif message_type == "interactive":
                    interactive = message.get("interactive") or {}
                    if interactive.get("type") == "button_reply":
                        text = (interactive.get("button_reply") or {}).get("title")
                    elif interactive.get("type") == "list_reply":
                        text = (interactive.get("list_reply") or {}).get("title")

                messages.append(
                    {
                        "from_phone": message.get("from"),
                        "message_id": message.get("id"),
                        "type": message_type,
                        "text": text,
                        "profile_name": profile_name,
                    }
                )
    return messages
