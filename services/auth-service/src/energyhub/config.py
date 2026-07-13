"""Configuração do **auth-service** (Fase 15).

Twelve-factor: tudo por variável de ambiente. Além das settings herdadas do monólito, cada
microsserviço declara sua **identidade** (`app_name`), sua **porta** (`app_port`, única por serviço)
e o **endpoint de descoberta** (Consul), para se registrar e ser resolvido por nome.
"""

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
    """Configurações do serviço, carregadas de variáveis de ambiente e do `.env`."""

    # Identidade do serviço (Fase 15)
    app_name: str = "auth-service"
    app_port: int = 8001
    app_version: str = "0.15.0"
    environment: str = "development"
    debug: bool = False

    # Descoberta de serviço — Consul (Fase 15)
    consul_host: str = "consul"
    consul_port: int = 8500
    # Endereço com que o serviço se anuncia no Consul (nome do serviço na rede do compose).
    service_host: str = "auth-service"

    # Banco PRÓPRIO do serviço (auth-service é dono de users/roles/permissions).
    database_url: str = ""  # sem credencial embutida — vem de env/secret

    # Segurança / JWT
    secret_key: str = ""  # sem default placeholder — vem de env/secret
    internal_api_key: str = ""  # credencial inter-servico p/ rotas /internal/* (X-Internal-Api-Key)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Cache (Redis) — compartilhado (stateless), não é banco de dados de outro serviço.
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # Mensageria (RabbitMQ) — publicação de eventos de usuário (best-effort).
    rabbitmq_url: str = ""  # sem credencial embutida — vem de env/secret
    kafka_bootstrap_servers: str = "kafka:29092"

    # Busca — não usada pelo auth-service; mantida para compatibilidade de import do kernel.
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
        """URL de conexão `redis://[:senha@]host:porta/db`, derivada das settings."""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância de configurações (memoizada)."""
    return Settings()


settings = get_settings()
