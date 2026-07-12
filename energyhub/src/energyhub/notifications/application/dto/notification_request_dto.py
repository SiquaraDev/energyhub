"""DTO de request de notificação."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from energyhub.notifications.domain.entity.notification_status import NotificationStatus
from energyhub.shared.application.validation.validators import validate_non_empty


class NotificationRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar uma notificação."""

    user_id: UUID = Field(
        ...,
        description="Identificador do usuário destinatário",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Título da notificação",
        examples=["Fatura disponível"],
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Conteúdo da notificação",
        examples=["Sua fatura de energia já está disponível para consulta."],
    )
    status: NotificationStatus = Field(
        NotificationStatus.PENDING,
        description="Estado do ciclo de vida da notificação",
        examples=["PENDING"],
    )

    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str) -> str:
        return validate_non_empty(value)

    @field_validator("message")
    @classmethod
    def _validate_message(cls, value: str) -> str:
        return validate_non_empty(value)
