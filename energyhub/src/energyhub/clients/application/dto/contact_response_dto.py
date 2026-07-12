"""DTO de resposta de contato."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from energyhub.clients.domain.entity.contact_type import ContactType
from energyhub.shared.application.dto.base_dto import BaseDTO


class ContactResponseDTO(BaseDTO):
    """Representação de saída de um contato (inclui id/timestamps do `BaseDTO`)."""

    client_id: UUID = Field(
        description="Id do cliente ao qual o contato pertence",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    name: str = Field(description="Nome do contato", examples=["Joao da Silva"])
    type: ContactType = Field(
        description="Tipo do contato (PRIMARY, BILLING, ...)", examples=[ContactType.PRIMARY]
    )
    email: str | None = Field(
        default=None, description="E-mail do contato", examples=["usuario@energyhub.example"]
    )
    phone: str | None = Field(
        default=None, description="Telefone do contato", examples=["+55 11 99999-0000"]
    )
    position: str | None = Field(
        default=None, description="Cargo/posição do contato", examples=["Gerente de Operações"]
    )
