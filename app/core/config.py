from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "sqlite:////tmp/leadflow_demo.db"


class Settings(BaseSettings):
    """Configurações centralizadas do Évora LeadFlow.

    A demo premium foi deixada tolerante a variáveis vazias no Vercel.
    Isso evita erro 500 quando uma variável opcional é criada sem valor
    ou quando um DATABASE_URL placeholder é usado antes do PostgreSQL real.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Évora LeadFlow", alias="APP_NAME")
    app_env: str = Field(default="demo", alias="APP_ENV")
    timezone: str = Field(default="America/Sao_Paulo", alias="TIMEZONE")
    enable_scheduler: bool = Field(default=False, alias="ENABLE_SCHEDULER")
    daily_reminder_hour: int = Field(default=8, alias="DAILY_REMINDER_HOUR")

    # Para a demo na Vercel, SQLite em /tmp evita depender de PostgreSQL nesta fase.
    # Na versão final, configure DEMO_FORCE_SQLITE=false e um PostgreSQL gerenciado.
    database_url: str = Field(default=DEFAULT_DATABASE_URL, alias="DATABASE_URL")
    demo_force_sqlite: bool = Field(default=True, alias="DEMO_FORCE_SQLITE")
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    dashboard_username: str = Field(default="evora", alias="DASHBOARD_USERNAME")
    dashboard_password: str = Field(default="leadflow-demo", alias="DASHBOARD_PASSWORD")
    disable_dashboard_auth: bool = Field(default=False, alias="DISABLE_DASHBOARD_AUTH")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5.5", alias="OPENAI_MODEL")

    whatsapp_verify_token: str = Field(default="evora_leadflow_verify_token_change_me", alias="WHATSAPP_VERIFY_TOKEN")
    whatsapp_access_token: str | None = Field(default=None, alias="WHATSAPP_ACCESS_TOKEN")
    whatsapp_phone_number_id: str | None = Field(default=None, alias="WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_app_secret: str | None = Field(default=None, alias="WHATSAPP_APP_SECRET")
    whatsapp_graph_version: str = Field(default="v23.0", alias="WHATSAPP_GRAPH_VERSION")

    default_manager_phone: str | None = Field(default="5516999990000", alias="DEFAULT_MANAGER_PHONE")
    cron_secret: str | None = Field(default=None, alias="CRON_SECRET")

    @field_validator("enable_scheduler", "disable_dashboard_auth", "demo_force_sqlite", mode="before")
    @classmethod
    def _blank_or_text_to_bool(cls, value: Any, info) -> bool:
        if value is None or value == "":
            return True if info.field_name == "demo_force_sqlite" else False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "t", "yes", "y", "sim", "s", "on"}:
                return True
            if normalized in {"0", "false", "f", "no", "n", "nao", "não", "off"}:
                return False
        return bool(value)

    @field_validator("daily_reminder_hour", mode="before")
    @classmethod
    def _blank_to_default_hour(cls, value: Any) -> int:
        if value is None or value == "":
            return 8
        return int(value)

    @field_validator(
        "app_name",
        "app_env",
        "timezone",
        "database_url",
        "redis_url",
        "dashboard_username",
        "dashboard_password",
        "openai_model",
        "whatsapp_verify_token",
        "whatsapp_graph_version",
        mode="before",
    )
    @classmethod
    def _blank_to_defaults(cls, value: Any, info):
        defaults = {
            "app_name": "Évora LeadFlow",
            "app_env": "demo",
            "timezone": "America/Sao_Paulo",
            "database_url": DEFAULT_DATABASE_URL,
            "redis_url": "redis://redis:6379/0",
            "dashboard_username": "evora",
            "dashboard_password": "leadflow-demo",
            "openai_model": "gpt-5.5",
            "whatsapp_verify_token": "evora_leadflow_verify_token_change_me",
            "whatsapp_graph_version": "v23.0",
        }
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return defaults[info.field_name]
        return value

    @field_validator(
        "openai_api_key",
        "whatsapp_access_token",
        "whatsapp_phone_number_id",
        "whatsapp_app_secret",
        "default_manager_phone",
        "cron_secret",
        mode="before",
    )
    @classmethod
    def _blank_to_none(cls, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str) and value.strip() == "":
            return None
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
