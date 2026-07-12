"""DTO de request de contato."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from energyhub.clients.domain.entity.contact_type import ContactType
from energyhub.shared.application.validation.validators import validate_email, validate_non_empty


class ContactRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar um contato de cliente."""

    name: str = Field(..., description="Nome do contato")
    type: ContactType = Field(..., description="Tipo do contato (PRIMARY, BILLING, ...)")
    email: str | None = Field(None, description="E-mail do contato")
    phone: str | None = Field(None, description="Telefone do contato")
    position: str | None = Field(None, description="Cargo/posição do contato")

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return validate_non_empty(value)

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str | None) -> str | None:
        return validate_email(value) if value is not None else value
