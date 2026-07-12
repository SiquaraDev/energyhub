"""Cliente HTTP para o contexto **Clients** (Fase 15).

Preserva a direção Contracts → Clients: quando o serviço de contratos precisa de dados de cliente
(que antes viriam de uma leitura in-process / FK de banco), ele os obtém do `client-service` por HTTP,
com a mesma política de resiliência (timeout + retry + fallback).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from energyhub.service_clients.base import ServiceClient


class ClientClient(ServiceClient):
    """Expõe as operações que este serviço precisa do contexto Clients."""

    def __init__(self) -> None:
        super().__init__("client-service", 8002)

    async def get_client_by_id(self, client_id: UUID | str) -> dict[str, Any] | None:
        """Busca um cliente pelo id no client-service; `None` se ausente/indisponível."""
        return await self._get(f"/internal/clients/{client_id}")


client_client = ClientClient()
