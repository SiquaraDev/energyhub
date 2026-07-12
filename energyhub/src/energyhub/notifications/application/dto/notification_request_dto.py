"""DTO de request de notificação."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from energyhub.notifications.domain.entity.notification_status import NotificationStatus
from energyhub.shared.application.validation.validators import validate_non_empty


class NotificationRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar uma notificação."""

    user_id: UUID = Field(..., description="Identificador do usuário destinatário")
    title: str = Field(..., description="Título da notificação")
    message: str = Field(..., description="Conteúdo da notificação")
    status: NotificationStatus = Field(
        NotificationStatus.PENDING, description="Estado do ciclo de vida da notificação"
    )

    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str) -> str:
        return validate_non_empty(value)

    @field_validator("message")
    @classmethod
    def _validate_message(cls, value: str) -> str:
        return validate_non_empty(value)
