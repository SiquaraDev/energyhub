"""Configuração da aplicação via Pydantic Settings (variáveis de ambiente / .env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação, carregadas de variáveis de ambiente e do arquivo .env."""

    app_name: str = "EnergyHub"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://energyhub:energyhub123@localhost:5432/energyhub"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Cache (Redis) — Fase 9. `redis_url` é derivado de host/porta/db (ver propriedade abaixo).
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # Mensageria — Fase 10. RabbitMQ (workflows por entidade) + Kafka (streams de alto volume).
    rabbitmq_url: str = "amqp://energyhub:energyhub123@localhost:5672/"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "energyhub"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

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
