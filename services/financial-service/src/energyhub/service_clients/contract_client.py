"""Cliente HTTP para o contexto **Contracts** (Fase 15) — usado pelo financial-service.

Preserva a direção Financial → Contracts: dados de contrato vêm do `contract-service` por HTTP, com
resiliência (timeout + retry + fallback).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from energyhub.service_clients.base import ServiceClient


class ContractClient(ServiceClient):
    def __init__(self) -> None:
        super().__init__("contract-service", 8003)

    async def get_contract_by_id(self, contract_id: UUID | str) -> dict[str, Any] | None:
        return await self._get(f"/internal/contracts/{contract_id}")


contract_client = ContractClient()
