"""Consumidor de eventos Kafka (Fase 10) — consumo por tópico dentro do consumer group.

`KafkaEventConsumer` expõe métodos por tópico (`consume_user_events`, `consume_client_events`,
`consume_financial_events`) que assinam o tópico sob `settings.kafka_group_id`, desserializam cada
mensagem JSON e a repassam ao handler. O consumidor é sempre parado num bloco `finally`, liberando
offsets/conexões independentemente de como o laço termina (fim natural ou cancelamento).
"""

from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiokafka import AIOKafkaConsumer

from energyhub.config.settings import settings
from energyhub.shared.infrastructure.messaging.kafka_config import KafkaConfig

logger = logging.getLogger(__name__)

Handler = Callable[[dict[str, Any]], Awaitable[None]]


class KafkaEventConsumer:
    """Consome eventos de um tópico no grupo `settings.kafka_group_id`, desserializando JSON."""

    async def consume_user_events(self, handler: Handler) -> None:
        """Consome o tópico `user-events`."""
        await self._consume(KafkaConfig.USER_EVENTS, handler)

    async def consume_client_events(self, handler: Handler) -> None:
        """Consome o tópico `client-events`."""
        await self._consume(KafkaConfig.CLIENT_EVENTS, handler)

    async def consume_financial_events(self, handler: Handler) -> None:
        """Consome o tópico `financial-events`."""
        await self._consume(KafkaConfig.FINANCIAL_EVENTS, handler)

    async def _consume(self, topic: str, handler: Handler) -> None:
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_group_id,
            value_deserializer=lambda raw: json.loads(raw.decode()),
            auto_offset_reset="earliest",
        )
        await consumer.start()
        logger.info("KafkaEventConsumer assinando '%s' (grupo=%s)", topic, settings.kafka_group_id)
        try:
            async for message in consumer:
                await handler(message.value)
        finally:
            await consumer.stop()
