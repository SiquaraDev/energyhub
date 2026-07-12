"""DTO de filtro (critérios opcionais) para busca de `Client`."""

from __future__ import annotations

from pydantic import BaseModel, Field

from energyhub.clients.domain.entity.contact_type import ContactType


class ClientFilterDTO(BaseModel):
    """Critérios opcionais de filtragem de clientes (campos não informados são ignorados)."""

    cnpj: str | None = Field(
        default=None, description="Filtra pelo CNPJ do cliente", examples=["11222333000181"]
    )
    corporate_name: str | None = Field(
        default=None,
        description="Filtra pela razão social do cliente",
        examples=["Usina Solar Alpha Ltda"],
    )
    active: bool | None = Field(
        default=None, description="Filtra por clientes ativos/inativos", examples=[True]
    )
    city: str | None = Field(
        default=None, description="Filtra pela cidade do cliente", examples=["São Paulo"]
    )
    state: str | None = Field(
        default=None, description="Filtra pela UF/estado do cliente", examples=["SP"]
    )
    contact_type: ContactType | None = Field(
        default=None,
        description="Filtra por clientes que possuem contato do tipo informado",
        examples=[ContactType.PRIMARY],
    )
