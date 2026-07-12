"""Cliente HTTP para o contexto **Clients** (Fase 15) — usado pelo financial-service.

Preserva a direção Financial → Clients (uma fatura referencia um cliente): dados de cliente vêm do
`client-service` por HTTP, com resiliência (timeout + retry + fallback).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from energyhub.service_clients.base import ServiceClient


class ClientClient(ServiceClient):
    def __init__(self) -> None:
        super().__init__("client-service", 8002)

    async def get_client_by_id(self, client_id: UUID | str) -> dict[str, Any] | None:
        return await self._get(f"/internal/clients/{client_id}")


client_client = ClientClient()
