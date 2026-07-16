"""Consumidor de auditoria (RabbitMQ) — Fase 10.

`AuditConsumer` consome a fila de auditoria e persiste um `AuditLog` por evento via
`AuditLogRepository`. Roda off-request: abre a sua própria sessão por mensagem (não há a fronteira
transacional do `get_session`), portanto faz `commit` explícito. Usa `prefetch_count=1` e ack
baseado no sucesso do processamento (`message.process`) para at-least-once com redelivery na falha.
"""

from __future__ import annotations

import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from energyhub.audit.domain.entity.audit_action import AuditAction
from energyhub.audit.domain.entity.audit_log import AuditLog
from energyhub.audit.infrastructure.persistence.audit_log_repository import AuditLogRepository
from energyhub.shared.infrastructure.messaging.audit_event import AuditEvent
from energyhub.shared.infrastructure.messaging.rabbitmq_config import RabbitMQConfig
from energyhub.shared.infrastructure.persistence.database import async_session_maker

logger = logging.getLogger(__name__)


class AuditConsumer:
    """Persiste um `AuditLog` para cada evento recebido na fila de auditoria."""

    async def handle_message(self, message: AbstractIncomingMessage) -> None:
        """Reconstrói o `AuditEvent`, monta o `AuditLog` e persiste (commit próprio)."""
        async with message.process(requeue=True):  # ack no sucesso; requeue na falha
            payload = json.loads(message.body.decode())
            event = AuditEvent.model_validate(payload)
            async with async_session_maker() as session:
                repository = AuditLogRepository(session)
                audit_log = AuditLog(
                    user_id=event.user_id,
                    action=AuditAction(event.action),
                    entity_type=event.entity_type,
                    entity_id=event.entity_id,
                    details=event.details,
                    timestamp=event.timestamp,
                )
                await repository.save(audit_log)
                await session.commit()
            logger.info(
                "AuditLog persistido: action=%s entity=%s id=%s",
                event.action,
                event.entity_type,
                event.entity_id,
            )

    async def start_consuming(self) -> None:
        """Declara a fila de auditoria durável, fixa prefetch=1 e consome até ser cancelado.

        **Roda até o cancelamento** (a task de fundo do lifespan chama `consumer_task.cancel()` no
        shutdown). Isso é essencial: `queue.consume` apenas REGISTRA o callback e retorna de
        imediato — se esta corrotina terminasse aí, a task completaria, a `connection` (única
        referência viva) seria coletada e a assinatura morreria silenciosamente, deixando a fila
        com **0 consumers** e a trilha de auditoria vazia. Manter a corrotina suspensa preserva a
        conexão; o `finally` a fecha de forma limpa quando o shutdown cancela a task.
        """
        connection = await aio_pika.connect_robust(RabbitMQConfig.get_url())
        try:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue(RabbitMQConfig.AUDIT_QUEUE, durable=True)
            await queue.consume(self.handle_message)
            logger.info("AuditConsumer assinando a fila '%s'", RabbitMQConfig.AUDIT_QUEUE)
            await asyncio.Future()  # suspende até o cancelamento no shutdown
        finally:
            await connection.close()
