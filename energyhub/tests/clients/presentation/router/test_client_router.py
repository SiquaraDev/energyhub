"""Teste de INTEGRAÇÃO de API do fluxo de clientes (Fase 13 · task 5.4).

Sobe a aplicação FastAPI real (`TestClient` → lifespan: banco, cache, mensageria...), autentica no
endpoint de login e cria um cliente com token `Bearer`, validando `201` e o corpo da resposta.

Requer a infraestrutura acessível ao processo de teste **e** o seed do admin (migrations 0008/0009).
No Windows (host→container falha para o Postgres), rode in-container apontando `DATABASE_URL` para a
rede Docker. A fixture `client` pula automaticamente se a aplicação não subir; e o teste pula se o
login não estiver disponível (seed ausente).
"""

from __future__ import annotations

import random
from typing import Any

import pytest

pytestmark = pytest.mark.integration

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ChangeMe123!"  # rotacionar antes de produção


def _valid_cnpj() -> str:
    """Gera um CNPJ sintaticamente válido (dígitos verificadores corretos), único por execução."""
    base = [random.randint(0, 9) for _ in range(12)]

    def _check_digit(digits: list[int], weights: list[int]) -> int:
        total = sum(d * w for d, w in zip(digits, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    first = _check_digit(base, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    second = _check_digit(base + [first], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return "".join(str(d) for d in [*base, first, second])


def _login(api: Any) -> str | None:
    response = api.post(
        "/api/v1/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    )
    if response.status_code != 200:
        return None
    return str(response.json()["access_token"])


def test_should_create_client_when_authenticated(client: Any) -> None:
    token = _login(client)
    if token is None:
        pytest.skip("login indisponível (seed do admin/infra ausente)")

    headers = {"Authorization": f"Bearer {token}"}
    cnpj = _valid_cnpj()
    payload = {"cnpj": cnpj, "corporate_name": "Cliente Integração Fase 13", "city": "Santos"}

    response = client.post("/api/v1/clients", json=payload, headers=headers)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["cnpj"] == cnpj
    assert body["corporate_name"] == "Cliente Integração Fase 13"
    assert body["id"]

    # Limpa o cliente criado (evita poluir o banco compartilhado entre execuções).
    client.delete(f"/api/v1/clients/{body['id']}", headers=headers)
