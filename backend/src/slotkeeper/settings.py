"""環境ごとの接続情報を起動時に固定する。"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """秘密と公開設定を環境変数から取得する。"""

    model_config = SettingsConfigDict(env_prefix="SLOT_")
    environment: str = "local"
    database_url: str = "postgresql://slotkeeper:local-only@db:5432/slotkeeper"
    database_mode: str = "postgres"
    dsql_host: str = ""
    region: str = "ap-northeast-1"
    database_user: str = "slotkeeper_app"
    issuer: str = "http://localhost:8080/realms/slotkeeper"
    jwks_url: str = "http://oidc:8080/realms/slotkeeper/protocol/openid-connect/certs"
    client_id: str = "slotkeeper"
    auth_mode: str = "oidc"
    cors_origin: str = "http://localhost:4321"


@lru_cache
def settings() -> Settings:
    """同じプロセスでは同一の設定を利用する。"""
    return Settings()
