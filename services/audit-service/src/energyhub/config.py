"""Configuração do **audit-service** (Fase 15)."""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# --- Guarda de credenciais de producao (harden-security-credentials) ---------------------------
_KNOWN_PLACEHOLDERS = ("change-me-in-production", "energyhub123", "admin", "ChangeMe123!")


def _enforce_production_credentials(environment: str, credentials: dict[str, str]) -> None:
    """Em producao, aborta o boot se alguma credencial estiver vazia ou com placeholder."""
    if environment.strip().lower() != "production":
        return
    problems = [
        name
        for name, value in credentials.items()
        if not value or any(ph in value for ph in _KNOWN_PLACEHOLDERS)
    ]
    if problems:
        raise RuntimeError(
            "Boot em producao abortado - credenciais inseguras (vazias ou com placeholder): "
            + ", ".join(problems)
        )


class Settings(BaseSettings):
    """Configurações do serviço de auditoria (consumidor de eventos + API append-only)."""

    app_name: str = "audit-service"
    app_port: int = 8005
    app_version: str = "0.15.0"
    environment: str = "development"
    debug: bool = False

    consul_host: str = "consul"
    consul_port: int = 8500
    service_host: str = "audit-service"

    # Auth para os endpoints protegidos do router (não há upstream síncrono de negócio).
    auth_service_host: str = "auth-service"
    auth_service_port: int = 8001

    database_url: str = ""  # sem credencial embutida — vem de env/secret

    secret_key: str = ""  # sem default placeholder — vem de env/secret
    internal_api_key: str = ""  # credencial inter-servico p/ rotas /internal/* (X-Internal-Api-Key)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Barramento de eventos (RabbitMQ) — o audit-service CONSOME eventos daqui.
    rabbitmq_url: str = ""  # sem credencial embutida — vem de env/secret
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    kafka_bootstrap_servers: str = "kafka:29092"
    elasticsearch_url: str = "http://elasticsearch:9200"
    elasticsearch_timeout: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def _guard_credentials(self) -> "Settings":
        _enforce_production_credentials(
            self.environment,
            {"SECRET_KEY": self.secret_key, "DATABASE_URL": self.database_url},
        )
        return self

    @property
    def redis_url(self) -> str:
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
