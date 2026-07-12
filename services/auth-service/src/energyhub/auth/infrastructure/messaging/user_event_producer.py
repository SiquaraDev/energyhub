"""Produtor de eventos de usuário (RabbitMQ) — Fase 10.

`UserEventProducer` subclasse `EventProducer` e expõe métodos tipados por evento do ciclo de vida
de usuários, publicando o payload na fila correspondente do `RabbitMQConfig`.
"""

from __future__ import annotations

from uuid import UUID

from energyhub.auth.application.dto.user_response_dto import UserResponseDTO
from energyhub.shared.infrastructure.messaging.event_producer import EventProducer
from energyhub.shared.infrastructure.messaging.rabbitmq_config import RabbitMQConfig


class UserEventProducer(EventProducer):
    """Publica eventos de criação/atualização/remoção de usuários nas suas filas."""

    async def publish_user_created(self, user: UserResponseDTO) -> None:
        """Publica o usuário criado em `USER_CREATED_QUEUE`."""
        await self.publish(RabbitMQConfig.USER_CREATED_QUEUE, user.model_dump(mode="json"))

    async def publish_user_updated(self, user: UserResponseDTO) -> None:
        """Publica o usuário atualizado em `USER_UPDATED_QUEUE`."""
        await self.publish(RabbitMQConfig.USER_UPDATED_QUEUE, user.model_dump(mode="json"))

    async def publish_user_deleted(self, user_id: UUID) -> None:
        """Publica a remoção (apenas o id) em `USER_DELETED_QUEUE`."""
        await self.publish(RabbitMQConfig.USER_DELETED_QUEUE, {"id": str(user_id)})


#: Instância compartilhada (conexão robusta reutilizada entre requisições); encerrada no shutdown.
user_event_producer = UserEventProducer()
