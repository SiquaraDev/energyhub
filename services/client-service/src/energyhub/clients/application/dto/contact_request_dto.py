"""DTO de request de contato."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from energyhub.clients.domain.entity.contact_type import ContactType
from energyhub.shared.application.validation.validators import validate_email, validate_non_empty


class ContactRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar um contato de cliente."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nome do contato",
        examples=["Joao da Silva"],
    )
    type: ContactType = Field(
        ...,
        description="Tipo do contato (PRIMARY, BILLING, ...)",
        examples=[ContactType.PRIMARY],
    )
    email: str | None = Field(
        None,
        max_length=320,
        description="E-mail do contato",
        examples=["usuario@energyhub.example"],
    )
    phone: str | None = Field(
        None, max_length=32, description="Telefone do contato", examples=["+55 11 99999-0000"]
    )
    position: str | None = Field(
        None,
        max_length=120,
        description="Cargo/posição do contato",
        examples=["Gerente de Operações"],
    )

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return validate_non_empty(value)

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str | None) -> str | None:
        return validate_email(value) if value is not None else value
