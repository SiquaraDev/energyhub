"""Topologia de tópicos do Kafka (Fase 10).

`KafkaConfig` declara os **tópicos de eventos de alto volume** com partições/replicação por tópico
(o tópico financeiro usa mais partições para absorver maior throughput) e os cria de forma
**idempotente** (`create_topics` tolera tópicos já existentes, sem falhar em re-execuções).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import TopicAlreadyExistsError

from energyhub.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TopicSpec:
    """Especificação de um tópico Kafka: nome, nº de partições e fator de replicação."""

    name: str
    partitions: int
    replication_factor: int


class KafkaConfig:
    """Tópicos de eventos de alto volume + criação idempotente."""

    USER_EVENTS = "user-events"
    CLIENT_EVENTS = "client-events"
    CONTRACT_EVENTS = "contract-events"
    FINANCIAL_EVENTS = "financial-events"

    #: Partições dimensionadas por throughput esperado; replicação 1 (dev single-node).
    TOPICS: tuple[TopicSpec, ...] = (
        TopicSpec(USER_EVENTS, partitions=3, replication_factor=1),
        TopicSpec(CLIENT_EVENTS, partitions=3, replication_factor=1),
        TopicSpec(CONTRACT_EVENTS, partitions=3, replication_factor=1),
        TopicSpec(FINANCIAL_EVENTS, partitions=6, replication_factor=1),
    )

    @staticmethod
    async def create_topics() -> None:
        """Cria os tópicos declarados; tolera (por tópico) os que já existem. Idempotente."""
        admin = AIOKafkaAdminClient(bootstrap_servers=settings.kafka_bootstrap_servers)
        await admin.start()
        try:
            for spec in KafkaConfig.TOPICS:
                new_topic = NewTopic(
                    name=spec.name,
                    num_partitions=spec.partitions,
                    replication_factor=spec.replication_factor,
                )
                try:
                    await admin.create_topics([new_topic])
                    logger.info(
                        "Tópico Kafka criado: %s (partições=%d)", spec.name, spec.partitions
                    )
                except TopicAlreadyExistsError:
                    logger.info("Tópico Kafka já existe: %s", spec.name)
        finally:
            await admin.close()
