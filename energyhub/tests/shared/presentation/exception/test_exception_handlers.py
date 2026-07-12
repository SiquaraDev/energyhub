"""Testes unitários dos exception handlers (mapeamento domínio → HTTP)."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

from fastapi.exceptions import RequestValidationError

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException
from energyhub.shared.domain.exception.domain_exception import DomainException
from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)
from energyhub.shared.domain.exception.validation_exception import ValidationException
from energyhub.shared.presentation.exception.domain_exception_handler import (
    domain_exception_handler,
)
from energyhub.shared.presentation.exception.global_exception_handler import (
    global_exception_handler,
)
from energyhub.shared.presentation.exception.request_validation_exception_handler import (
    request_validation_exception_handler,
)


def _request(path: str = "/api/v1/clients") -> Any:
    return SimpleNamespace(url=SimpleNamespace(path=path))


def _body(response: Any) -> dict[str, Any]:
    return json.loads(bytes(response.body).decode())


async def test_not_found_maps_to_404() -> None:
    response = await domain_exception_handler(
        _request(), ResourceNotFoundException("cliente não encontrado")
    )
    assert response.status_code == 404
    body = _body(response)
    assert body["error_code"] == "RESOURCE_NOT_FOUND"
    assert body["path"] == "/api/v1/clients"


async def test_business_rule_maps_to_409() -> None:
    response = await domain_exception_handler(_request(), BusinessRuleException("já existe"))
    assert response.status_code == 409


async def test_validation_maps_to_422() -> None:
    response = await domain_exception_handler(_request(), ValidationException("inválido"))
    assert response.status_code == 422


async def test_generic_domain_error_maps_to_422() -> None:
    response = await domain_exception_handler(_request(), DomainException("erro genérico"))
    assert response.status_code == 422


async def test_global_handler_maps_to_500() -> None:
    response = await global_exception_handler(_request(), RuntimeError("boom"))
    assert response.status_code == 500
    body = _body(response)
    assert body["error_code"] == "INTERNAL_SERVER_ERROR"


async def test_request_validation_maps_to_400_with_field_errors() -> None:
    exc = RequestValidationError(
        [{"loc": ("body", "cnpj"), "msg": "Field required", "type": "missing"}]
    )
    response = await request_validation_exception_handler(_request(), exc)
    assert response.status_code == 400
    body = _body(response)
    assert body["errors"][0]["field"] == "cnpj"
    assert body["errors"][0]["message"] == "Field required"
