"""DTO de resposta de cliente."""

from __future__ import annotations

from pydantic import Field

from energyhub.clients.application.dto.contact_response_dto import ContactResponseDTO
from energyhub.shared.application.dto.base_dto import BaseDTO


class ClientResponseDTO(BaseDTO):
    """Representação de saída de um cliente (inclui id/timestamps do `BaseDTO` e contatos)."""

    cnpj: str
    corporate_name: str
    trade_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    active: bool = True
    contacts: list[ContactResponseDTO] = Field(default_factory=list)
