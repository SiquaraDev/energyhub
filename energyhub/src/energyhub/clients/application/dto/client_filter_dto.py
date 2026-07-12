"""DTO de filtro (critérios opcionais) para busca de `Client`."""

from __future__ import annotations

from pydantic import BaseModel

from energyhub.clients.domain.entity.contact_type import ContactType


class ClientFilterDTO(BaseModel):
    """Critérios opcionais de filtragem de clientes (campos não informados são ignorados)."""

    cnpj: str | None = None
    corporate_name: str | None = None
    active: bool | None = None
    city: str | None = None
    state: str | None = None
    contact_type: ContactType | None = None
