"""Produtor de eventos de auditoria (change `fix-microservices-gaps`).

A fila `audit` é durável e consumida pelo `AuditConsumer` desde a Fase 10, mas nenhum código
publicava nela — a trilha de auditoria ficava vazia. Este produtor fecha a metade que faltava,
reusando o `EventProducer` base (conexão robusta preguiçosa, fila durável, entrega persistente).
"""

from __future__ import annotations

from energyhub.shared.infrastructure.messaging.audit_event import AuditEvent
from energyhub.shared.infrastructure.messaging.event_producer import EventProducer
from energyhub.shared.infrastructure.messaging.rabbitmq_config import RabbitMQConfig


class AuditEventProducer(EventProducer):
    """Publica `AuditEvent` na fila de auditoria."""

    async def publish_audit(self, event: AuditEvent) -> None:
        """Publica o evento em `AUDIT_QUEUE` (JSON, entrega persistente)."""
        await self.publish(RabbitMQConfig.AUDIT_QUEUE, event.model_dump(mode="json"))


#: Instância compartilhada (conexão robusta reutilizada); encerrada no shutdown.
audit_event_producer = AuditEventProducer()
