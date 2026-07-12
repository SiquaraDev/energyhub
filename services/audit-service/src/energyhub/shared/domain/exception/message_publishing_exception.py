"""Exceção de falha ao publicar mensagem em um broker (RabbitMQ/Kafka) — Fase 10."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.domain_exception import DomainException


class MessagePublishingException(DomainException):
    """Lançada quando a publicação de um evento no broker falha.

    Encadeada (`raise ... from erro`) a partir do erro original do cliente de mensageria, entrega
    ao chamador uma falha **tipada e de nível de domínio** em vez de um erro cru do broker. A
    publicação é um efeito colateral pós-commit: os serviços a tratam sem desfazer a escrita já
    persistida (ver `[[async-event-consumers]]` e a reliability da Fase 10).
    """

    error_code: ClassVar[str] = "MESSAGE_PUBLISHING_ERROR"
