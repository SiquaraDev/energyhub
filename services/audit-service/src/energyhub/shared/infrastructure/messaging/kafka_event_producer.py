"""Produtor de eventos Kafka (Fase 10) — publicação JSON com chave de partição.

`KafkaEventProducer` tem ciclo de vida explícito (`start`/`stop`) e uma primitiva
`publish(topic, key, message)` que serializa o valor em JSON, publica sob a `key` informada e
**aguarda o ack** do broker (`send_and_wait`). Eventos com a mesma chave caem na mesma partição,
preservando a ordem relativa. Falhas viram `MessagePublishingException` (após log).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer

from energyhub.config import settings
from energyhub.shared.domain.exception.message_publishing_exception import (
    MessagePublishingException,
)

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    """Ciclo de vida explícito (`start`/`stop`) + `publish(topic, key, message)` com ack."""

    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Cria e conecta o produtor async subjacente, se ainda não iniciado (idempotente)."""
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda value: json.dumps(value, default=str).encode(),
                key_serializer=lambda key: key.encode() if key is not None else None,
            )
            await self._producer.start()

    async def stop(self) -> None:
        """Fecha o produtor de forma limpa (chamado no shutdown da aplicação)."""
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

    async def publish(self, topic: str, key: str, message: dict[str, Any]) -> None:
        """Publica `message` (JSON) no `topic` sob `key` e aguarda o ack do broker."""
        try:
            await self.start()
            assert self._producer is not None
            await self._producer.send_and_wait(topic, value=message, key=key)
        except Exception as error:
            logger.error("Falha ao publicar no tópico '%s': %s", topic, error)
            raise MessagePublishingException(
                f"Falha ao publicar mensagem no tópico '{topic}'"
            ) from error


#: Instância compartilhada (produtor async reaproveitado entre requisições); parada no shutdown.
kafka_event_producer = KafkaEventProducer()
