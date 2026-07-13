"""Configuração da aplicação via Pydantic Settings (variáveis de ambiente / .env)."""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from energyhub.config.security_guard import enforce_production_credentials


class Settings(BaseSettings):
    """Configurações da aplicação, carregadas de variáveis de ambiente e do arquivo .env."""

    app_name: str = "EnergyHub"
    app_version: str = "0.12.0"  # versão atual (marco da fase); usada no `application_info`
    environment: str = "development"  # development | staging | production
    debug: bool = False
    # Credenciais SEM default placeholder (harden-security-credentials): o valor vem sempre de
    # variável de ambiente / secret. Vazio = "não configurado"; em `production` a guarda abaixo
    # aborta o boot (fail-fast), em dev/staging segue permissivo (conveniência local via `.env`).
    database_url: str = ""
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Cache (Redis) — Fase 9. `redis_url` é derivado de host/porta/db (ver propriedade abaixo).
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # Mensageria — Fase 10. RabbitMQ (workflows por entidade) + Kafka (streams de alto volume).
    # `rabbitmq_url` embute a senha → sem default placeholder (fornecida por env/secret).
    rabbitmq_url: str = ""
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "energyhub"

    # Busca — Fase 11. Elasticsearch (índice de leitura; o Postgres segue a fonte de verdade).
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_timeout: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def _guard_production_credentials(self) -> "Settings":
        """Em `production`, aborta o boot se alguma credencial estiver vazia ou com placeholder."""
        enforce_production_credentials(
            self.environment,
            {
                "SECRET_KEY": self.secret_key,
                "DATABASE_URL": self.database_url,
                "RABBITMQ_URL": self.rabbitmq_url,
            },
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
