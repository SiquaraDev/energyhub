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

    cnpj: str = Field(..., description="CNPJ do cliente (14 dígitos ou formatado)")
    corporate_name: str = Field(..., min_length=1, description="Razão social")
    trade_name: str | None = Field(None, description="Nome fantasia")
    email: str | None = Field(None, description="E-mail de contato do cliente")
    phone: str | None = Field(None, description="Telefone")
    address: str | None = Field(None, description="Endereço")
    city: str | None = Field(None, description="Cidade")
    state: str | None = Field(None, description="UF/estado")
    zip_code: str | None = Field(None, description="CEP")
    active: bool = Field(True, description="Indica se o cliente está ativo")

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
