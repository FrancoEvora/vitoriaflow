import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.core.config import get_settings

security = HTTPBasic(auto_error=False)


def require_dashboard_auth(credentials: HTTPBasicCredentials | None = Depends(security)) -> str:
    """Protege o painel com Basic Auth, mas permite demo pública se DISABLE_DASHBOARD_AUTH=true."""
    settings = get_settings()
    if settings.disable_dashboard_auth:
        return "demo"

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária",
            headers={"WWW-Authenticate": "Basic"},
        )

    username_ok = secrets.compare_digest(credentials.username, settings.dashboard_username)
    password_ok = secrets.compare_digest(credentials.password, settings.dashboard_password)
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
