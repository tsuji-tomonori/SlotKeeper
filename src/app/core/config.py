from __future__ import annotations

from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """環境ごとの接続情報を環境変数から取得します。"""

    model_config = SettingsConfigDict(env_prefix="SLOT_", extra="ignore")

    app_name: str = "SlotKeeper"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "local"

    database_url: str = "postgresql+psycopg://slotkeeper:local-only@db:5432/slotkeeper"
    database_mode: Literal["postgres", "dsql"] = "postgres"
    dsql_host: str = ""
    region: str = "ap-northeast-1"
    database_user: str = "slotkeeper_app"

    issuer: str = "http://localhost:8080/realms/slotkeeper"
    jwks_url: str = "http://oidc:8080/realms/slotkeeper/protocol/openid-connect/certs"
    client_id: str = "slotkeeper"
    auth_mode: Literal["oidc", "cognito"] = "oidc"
    cors_origin: str = "http://localhost:4321"

    @model_validator(mode="after")
    def validate_database_mode(self) -> Settings:
        if self.database_mode == "dsql" and not self.dsql_host:
            raise RuntimeError("SLOT_DSQL_HOST is required in dsql mode")
        return self


settings = Settings()
