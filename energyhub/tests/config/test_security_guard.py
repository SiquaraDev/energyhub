"""Testes da guarda de credenciais de produção (change `harden-security-credentials`).

Cobrem os cenários da spec `production-credential-validation`:
- placeholder conhecido em `production` aborta o boot;
- credencial vazia/ausente em `production` aborta o boot;
- perfis não-produção (`development`/`staging`) seguem permissivos (no-op).
"""

from __future__ import annotations

import pytest

from energyhub.config.security_guard import (
    InsecureCredentialError,
    enforce_production_credentials,
)


class TestProductionRejectsPlaceholders:
    """`production` rejeita qualquer credencial com valor placeholder conhecido."""

    def test_should_abort_when_secret_key_is_placeholder(self) -> None:
        with pytest.raises(InsecureCredentialError) as exc:
            enforce_production_credentials("production", {"SECRET_KEY": "change-me-in-production"})
        assert "SECRET_KEY" in str(exc.value)

    def test_should_abort_when_database_url_embeds_placeholder_password(self) -> None:
        with pytest.raises(InsecureCredentialError) as exc:
            enforce_production_credentials(
                "production",
                {
                    "DATABASE_URL": (
                        "postgresql+asyncpg://energyhub:energyhub123@postgres:5432/authdb"
                    )
                },
            )
        assert "DATABASE_URL" in str(exc.value)
        assert "energyhub123" in str(exc.value)

    def test_should_abort_when_rabbitmq_url_embeds_placeholder_password(self) -> None:
        with pytest.raises(InsecureCredentialError):
            enforce_production_credentials(
                "production",
                {"RABBITMQ_URL": "amqp://energyhub:energyhub123@rabbitmq:5672/"},
            )

    def test_should_report_every_offending_credential(self) -> None:
        with pytest.raises(InsecureCredentialError) as exc:
            enforce_production_credentials(
                "production",
                {
                    "SECRET_KEY": "change-me-in-production",
                    "RABBITMQ_URL": "amqp://energyhub:energyhub123@rabbitmq:5672/",
                },
            )
        message = str(exc.value)
        assert "SECRET_KEY" in message
        assert "RABBITMQ_URL" in message


class TestProductionRejectsEmpty:
    """`production` trata credencial vazia/ausente como inválida."""

    def test_should_abort_when_credential_is_empty_string(self) -> None:
        with pytest.raises(InsecureCredentialError) as exc:
            enforce_production_credentials("production", {"SECRET_KEY": ""})
        assert "SECRET_KEY" in str(exc.value)

    def test_should_abort_when_credential_is_none(self) -> None:
        with pytest.raises(InsecureCredentialError):
            enforce_production_credentials("production", {"DATABASE_URL": None})


class TestNonProductionIsPermissive:
    """A guarda só se aplica a `production`; demais perfis são no-op."""

    @pytest.mark.parametrize("environment", ["development", "staging", "local", "PRODUCTION_LIKE"])
    def test_should_not_raise_outside_production(self, environment: str) -> None:
        # Mesmo com todos os placeholders, um perfil não-produção passa sem erro.
        enforce_production_credentials(
            environment,
            {
                "SECRET_KEY": "change-me-in-production",
                "DATABASE_URL": "postgresql+asyncpg://energyhub:energyhub123@localhost/db",
                "RABBITMQ_URL": "",
            },
        )

    def test_should_pass_production_with_real_credentials(self) -> None:
        # Valores reais (sem placeholder, não-vazios) passam mesmo em produção.
        enforce_production_credentials(
            "production",
            {
                "SECRET_KEY": "b6c1f0a9e5d34c7f8a2b1e0d9c8f7a6b",
                "DATABASE_URL": (
                    "postgresql+asyncpg://energyhub:S3cur3-Rot8ted@postgres:5432/authdb"
                ),
                "RABBITMQ_URL": "amqp://energyhub:An0ther-S3cret@rabbitmq:5672/",
            },
        )

    def test_should_be_case_insensitive_on_environment(self) -> None:
        with pytest.raises(InsecureCredentialError):
            enforce_production_credentials("Production", {"SECRET_KEY": "energyhub123"})
