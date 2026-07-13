"""Guarda de credenciais para o perfil de produção (change `harden-security-credentials`).

Quando `environment == "production"`, o boot é **abortado** se qualquer credencial obrigatória
ainda estiver vazia/ausente ou contiver um placeholder herdado (ex.: `change-me-in-production`,
`energyhub123`). É uma defesa contra o erro mais provável — subir produção com um default esquecido.

Fora de produção (`development`/`staging`/local) a checagem é **no-op**: perfis locais seguem
permissivos, com valores de conveniência vindos do `.env`/compose. A guarda rejeita apenas o
conjunto explícito de placeholders conhecidos e valores vazios — nunca "senhas fracas" arbitrárias —
para não bloquear um boot legítimo por falso-positivo.
"""

from __future__ import annotations

# Valores placeholder herdados que NUNCA podem ir a produção.
KNOWN_PLACEHOLDERS: frozenset[str] = frozenset(
    {
        "change-me-in-production",
        "energyhub123",
        "admin",
        "ChangeMe123!",
    }
)


class InsecureCredentialError(RuntimeError):
    """Configuração insegura: credencial obrigatória vazia ou com placeholder em `production`."""


def _find_placeholder(value: str) -> str | None:
    """Retorna o primeiro placeholder conhecido contido em `value`, ou `None`."""
    for placeholder in KNOWN_PLACEHOLDERS:
        if placeholder in value:
            return placeholder
    return None


def enforce_production_credentials(environment: str, credentials: dict[str, str | None]) -> None:
    """Em `production`, rejeita credencial vazia/ausente ou com placeholder conhecido.

    `credentials` mapeia nome-lógico → valor (ex.: `{"SECRET_KEY": ..., "DATABASE_URL": ...}`).
    Levanta `InsecureCredentialError` (abortando o boot) se houver qualquer violação; caso
    contrário retorna silenciosamente. Fora de `production` é no-op.
    """
    if environment.strip().lower() != "production":
        return

    problems: list[str] = []
    for name, value in credentials.items():
        if value is None or value == "":
            problems.append(f"{name} está vazia/ausente")
            continue
        placeholder = _find_placeholder(value)
        if placeholder is not None:
            problems.append(f"{name} contém o placeholder proibido '{placeholder}'")

    if problems:
        raise InsecureCredentialError(
            "Boot em produção abortado — credenciais inseguras: " + "; ".join(problems) + ". "
            "Rotacione e forneça valores reais via secret/variável de ambiente "
            "(veja docs/runbook-security.md e .env.example)."
        )
