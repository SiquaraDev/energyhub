"""Consumidor de notificações (RabbitMQ) — Fase 10.

`NotificationConsumer` assina as filas relevantes para notificação (usuário criado, cliente criado,
contrato aprovado, fatura emitida). Ao iniciar, declara as filas duráveis, fixa `prefetch_count=1`
e registra um handler por evento. Cada mensagem é processada dentro de `message.process(...)`: o ack
ocorre **após** o processamento bem-sucedido; uma falha re-enfileira a mensagem (at-least-once).
"""

from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from energyhub.shared.infrastructure.messaging.rabbitmq_config import RabbitMQConfig

logger = logging.getLogger(__name__)

Handler = Callable[[dict[str, Any]], Awaitable[None]]


class NotificationConsumer:
    """Reage a eventos de domínio disparando notificações (efeito colateral off-request)."""

    async def handle_user_created(self, event: dict[str, Any]) -> None:
        """Trata `user.created` — dispara a notificação de boas-vindas ao usuário."""
        logger.info("Notificação: usuário criado id=%s", event.get("id"))

    async def handle_client_created(self, event: dict[str, Any]) -> None:
        """Trata `client.created` — notifica o cadastro de um novo cliente."""
        logger.info("Notificação: cliente criado id=%s", event.get("id"))

    async def handle_contract_approved(self, event: dict[str, Any]) -> None:
        """Trata `contract.approved` — notifica as partes da aprovação do contrato."""
        logger.info("Notificação: contrato aprovado id=%s", event.get("id"))

    async def handle_invoice_issued(self, event: dict[str, Any]) -> None:
        """Trata `invoice.issued` — notifica a emissão de uma fatura."""
        logger.info("Notificação: fatura emitida id=%s", event.get("id"))

    async def start_consuming(self) -> None:
        """Declara as filas duráveis, fixa prefetch=1 e registra um handler por evento."""
        connection = await aio_pika.connect_robust(RabbitMQConfig.get_url())
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        bindings: dict[str, Handler] = {
            RabbitMQConfig.USER_CREATED_QUEUE: self.handle_user_created,
            RabbitMQConfig.CLIENT_CREATED_QUEUE: self.handle_client_created,
            RabbitMQConfig.CONTRACT_APPROVED_QUEUE: self.handle_contract_approved,
            RabbitMQConfig.INVOICE_ISSUED_QUEUE: self.handle_invoice_issued,
        }
        for queue_name, handler in bindings.items():
            queue = await channel.declare_queue(queue_name, durable=True)
            await queue.consume(self._make_callback(handler))
        logger.info("NotificationConsumer assinando %d filas", len(bindings))

    @staticmethod
    def _make_callback(
        handler: Handler,
    ) -> Callable[[AbstractIncomingMessage], Awaitable[None]]:
        """Adapta um handler de payload num callback de mensagem com ack pós-processamento."""

        async def callback(message: AbstractIncomingMessage) -> None:
            async with message.process(requeue=True):  # ack no sucesso; requeue na falha
                event = json.loads(message.body.decode())
                await handler(event)

        return callback
