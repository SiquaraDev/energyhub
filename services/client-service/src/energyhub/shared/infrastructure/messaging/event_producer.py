"""Produtor base de eventos para RabbitMQ (Fase 10).

`EventProducer` encapsula a **conexão robusta** (reconexão automática), o canal e a primitiva
`publish(queue, message)`. A conexão é estabelecida **preguiçosamente** na primeira publicação;
a mensagem é serializada em JSON e publicada no *default exchange* com a routing key = nome da
fila, em modo **persistente** (`DeliveryMode.PERSISTENT`) para sobreviver a um restart do broker.
Falhas são encapsuladas em `MessagePublishingException` (encadeada do erro original), após log.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from energyhub.shared.domain.exception.message_publishing_exception import (
    MessagePublishingException,
)
from energyhub.shared.infrastructure.messaging.rabbitmq_config import RabbitMQConfig

logger = logging.getLogger(__name__)


class EventProducer:
    """Produtor genérico: conexão robusta preguiçosa + `publish` persistente reutilizável."""

    def __init__(self) -> None:
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractChannel | None = None

    async def connect(self) -> None:
        """Estabelece a conexão robusta e o canal, se ainda não abertos (idempotente)."""
        if self._connection is None or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(RabbitMQConfig.get_url())
            self._channel = await self._connection.channel()

    async def disconnect(self) -> None:
        """Fecha a conexão, se aberta (chamado no shutdown da aplicação)."""
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
        self._channel = None

    async def publish(self, queue: str, message: dict[str, Any]) -> None:
        """Serializa `message` (JSON) e publica na `queue` em modo persistente.

        Conecta preguiçosamente, declara a fila durável (idempotente) e publica no *default
        exchange* usando o nome da fila como routing key. Qualquer falha é logada e re-lançada
        como `MessagePublishingException` (encadeada do erro original).
        """
        try:
            await self.connect()
            assert self._channel is not None
            await self._channel.declare_queue(queue, durable=True)
            body = json.dumps(message, default=str).encode()
            await self._channel.default_exchange.publish(
                aio_pika.Message(body=body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key=queue,
            )
        except Exception as error:
            logger.error("Falha ao publicar na fila '%s': %s", queue, error)
            raise MessagePublishingException(
                f"Falha ao publicar mensagem na fila '{queue}'"
            ) from error
