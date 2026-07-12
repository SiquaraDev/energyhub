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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância de configurações (memoizada)."""
    return Settings()


settings = get_settings()
