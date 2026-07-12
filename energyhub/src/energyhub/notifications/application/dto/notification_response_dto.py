"""DTO de resposta de notificação."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from energyhub.notifications.domain.entity.notification_status import NotificationStatus
from energyhub.shared.application.dto.base_dto import BaseDTO


class NotificationResponseDTO(BaseDTO):
    """Representação de saída de uma notificação (inclui id/timestamps do `BaseDTO`)."""

    user_id: UUID = Field(
        ...,
        description="Identificador do usuário destinatário",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    title: str = Field(..., description="Título da notificação", examples=["Fatura disponível"])
    message: str = Field(
        ...,
        description="Conteúdo da notificação",
        examples=["Sua fatura de energia já está disponível para consulta."],
    )
    status: NotificationStatus = Field(
        NotificationStatus.PENDING,
        description="Estado do ciclo de vida da notificação",
        examples=["PENDING"],
    )
