"""Produtor de eventos de cliente (RabbitMQ) — Fase 10.

`ClientEventProducer` subclasse `EventProducer` e expõe métodos tipados para os eventos de cliente,
publicando o payload do DTO de resposta na fila correspondente do `RabbitMQConfig`.
"""

from __future__ import annotations

from energyhub.clients.application.dto.client_response_dto import ClientResponseDTO
from energyhub.shared.infrastructure.messaging.event_producer import EventProducer
from energyhub.shared.infrastructure.messaging.rabbitmq_config import RabbitMQConfig


class ClientEventProducer(EventProducer):
    """Publica eventos de criação/atualização de clientes nas suas filas."""

    async def publish_client_created(self, client: ClientResponseDTO) -> None:
        """Publica o cliente criado em `CLIENT_CREATED_QUEUE`."""
        await self.publish(RabbitMQConfig.CLIENT_CREATED_QUEUE, client.model_dump(mode="json"))

    async def publish_client_updated(self, client: ClientResponseDTO) -> None:
        """Publica o cliente atualizado em `CLIENT_UPDATED_QUEUE`."""
        await self.publish(RabbitMQConfig.CLIENT_UPDATED_QUEUE, client.model_dump(mode="json"))


#: Instância compartilhada (conexão robusta reutilizada entre requisições); encerrada no shutdown.
client_event_producer = ClientEventProducer()
