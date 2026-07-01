import hashlib
import hmac


def verify_meta_signature(app_secret: str | None, raw_body: bytes, signature_header: str | None) -> bool:
    """Valida X-Hub-Signature-256 enviado pela Meta, quando APP_SECRET estiver configurado."""

    if not app_secret:
        # Modo local/desenvolvimento. Em produção, configure WHATSAPP_APP_SECRET.
        return True

    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected = "sha256=" + hmac.new(
        key=app_secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)
