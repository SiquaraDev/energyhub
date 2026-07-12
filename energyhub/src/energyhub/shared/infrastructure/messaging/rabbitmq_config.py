"""Topologia de filas do RabbitMQ (Fase 10).

`RabbitMQConfig` centraliza os **nomes das filas** por evento de domínio (produtores e consumidores
referenciam a mesma constante, evitando divergência por digitação) e resolve a **URL do broker** a
partir de `settings.rabbitmq_url` (fonte única). `setup_queues()` declara todas as filas como
`durable=True` de forma **idempotente** — seguro re-executar no startup sem duplicar/alterar nada.
"""

from __future__ import annotations

import logging

import aio_pika

from energyhub.config.settings import settings

logger = logging.getLogger(__name__)


class RabbitMQConfig:
    """Constantes de nome de fila por evento de domínio + resolução da URL do broker."""

    # --- Eventos de usuário ---
    USER_CREATED_QUEUE = "user.created"
    USER_UPDATED_QUEUE = "user.updated"
    USER_DELETED_QUEUE = "user.deleted"

    # --- Eventos de cliente ---
    CLIENT_CREATED_QUEUE = "client.created"
    CLIENT_UPDATED_QUEUE = "client.updated"

    # --- Eventos de contrato ---
    CONTRACT_CREATED_QUEUE = "contract.created"
    CONTRACT_APPROVED_QUEUE = "contract.approved"

    # --- Eventos financeiros ---
    INVOICE_ISSUED_QUEUE = "invoice.issued"
    INVOICE_PAID_QUEUE = "invoice.paid"

    # --- Transversais ---
    NOTIFICATION_QUEUE = "notification"
    AUDIT_QUEUE = "audit"

    #: Todas as filas declaradas no startup (ver `setup_queues`).
    ALL_QUEUES: tuple[str, ...] = (
        USER_CREATED_QUEUE,
        USER_UPDATED_QUEUE,
        USER_DELETED_QUEUE,
        CLIENT_CREATED_QUEUE,
        CLIENT_UPDATED_QUEUE,
        CONTRACT_CREATED_QUEUE,
        CONTRACT_APPROVED_QUEUE,
        INVOICE_ISSUED_QUEUE,
        INVOICE_PAID_QUEUE,
        NOTIFICATION_QUEUE,
        AUDIT_QUEUE,
    )

    @staticmethod
    def get_url() -> str:
        """URL de conexão do broker, resolvida de `settings.rabbitmq_url` (fonte única)."""
        return settings.rabbitmq_url


async def setup_queues() -> None:
    """Declara todas as filas configuradas como duráveis. Idempotente (no-op se já existirem)."""
    connection = await aio_pika.connect_robust(RabbitMQConfig.get_url())
    async with connection:
        channel = await connection.channel()
        for queue_name in RabbitMQConfig.ALL_QUEUES:
            await channel.declare_queue(queue_name, durable=True)
    logger.info("Filas RabbitMQ declaradas (duráveis): %d", len(RabbitMQConfig.ALL_QUEUES))
