"""DTO de resposta de cliente."""

from __future__ import annotations

from pydantic import Field

from energyhub.clients.application.dto.contact_response_dto import ContactResponseDTO
from energyhub.shared.application.dto.base_dto import BaseDTO


class ClientResponseDTO(BaseDTO):
    """Representação de saída de um cliente (inclui id/timestamps do `BaseDTO` e contatos)."""

    cnpj: str = Field(description="CNPJ do cliente (14 dígitos)", examples=["11222333000181"])
    corporate_name: str = Field(description="Razão social", examples=["Usina Solar Alpha Ltda"])
    trade_name: str | None = Field(
        default=None, description="Nome fantasia", examples=["Usina Alpha"]
    )
    email: str | None = Field(
        default=None,
        description="E-mail de contato do cliente",
        examples=["usuario@energyhub.example"],
    )
    phone: str | None = Field(default=None, description="Telefone", examples=["+55 11 99999-0000"])
    address: str | None = Field(
        default=None, description="Endereço", examples=["Av. das Nações, 1000"]
    )
    city: str | None = Field(default=None, description="Cidade", examples=["São Paulo"])
    state: str | None = Field(default=None, description="UF/estado", examples=["SP"])
    zip_code: str | None = Field(default=None, description="CEP", examples=["01310-100"])
    active: bool = Field(
        default=True, description="Indica se o cliente está ativo", examples=[True]
    )
    contacts: list[ContactResponseDTO] = Field(
        default_factory=list, description="Contatos vinculados ao cliente"
    )
