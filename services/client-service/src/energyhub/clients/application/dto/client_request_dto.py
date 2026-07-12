"""DTO de request de cliente."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from energyhub.shared.application.validation.validators import (
    validate_cnpj,
    validate_email,
    validate_non_empty,
)


class ClientRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar um cliente.

    Os contatos são um sub-recurso: criados via `POST /clients/{id}/contacts` e retornados
    (aninhados) nos DTOs de resposta de cliente.
    """

    cnpj: str = Field(
        ...,
        min_length=14,
        max_length=18,
        description="CNPJ do cliente (14 dígitos ou formatado)",
        examples=["11222333000181"],
    )
    corporate_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Razão social",
        examples=["Usina Solar Alpha Ltda"],
    )
    trade_name: str | None = Field(
        None, max_length=255, description="Nome fantasia", examples=["Usina Alpha"]
    )
    email: str | None = Field(
        None,
        max_length=320,
        description="E-mail de contato do cliente",
        examples=["usuario@energyhub.example"],
    )
    phone: str | None = Field(
        None, max_length=32, description="Telefone", examples=["+55 11 99999-0000"]
    )
    address: str | None = Field(
        None, max_length=255, description="Endereço", examples=["Av. das Nações, 1000"]
    )
    city: str | None = Field(None, max_length=120, description="Cidade", examples=["São Paulo"])
    state: str | None = Field(None, max_length=64, description="UF/estado", examples=["SP"])
    zip_code: str | None = Field(None, max_length=16, description="CEP", examples=["01310-100"])
    active: bool = Field(True, description="Indica se o cliente está ativo", examples=[True])

    @field_validator("cnpj")
    @classmethod
    def _validate_cnpj(cls, value: str) -> str:
        return validate_cnpj(value)

    @field_validator("corporate_name")
    @classmethod
    def _validate_corporate_name(cls, value: str) -> str:
        return validate_non_empty(value)

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str | None) -> str | None:
        return validate_email(value) if value is not None else value
