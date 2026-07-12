"""Publicação de eventos como efeito colateral não-bloqueante (Fase 10).

A escrita é a fonte de verdade; a mensageria é *downstream*. `publish_safely` executa a publicação
**após** a escrita ter sido persistida e engole uma `MessagePublishingException` (apenas logando),
de modo que uma indisponibilidade do broker **não** desfaça a operação já concluída — ao custo de,
raramente, um evento perdido (inconsistência de dual-write aceita nesta fase; consumidores toleram
at-least-once). Ver `[[message-publishing-exception]]`.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable

from energyhub.shared.domain.exception.message_publishing_exception import (
    MessagePublishingException,
)

logger = logging.getLogger(__name__)


async def publish_safely(awaitable: Awaitable[None], *, event: str) -> None:
    """Aguarda a publicação; loga (sem propagar) se ela falhar, preservando a escrita já feita."""
    try:
        await awaitable
    except MessagePublishingException as error:
        logger.warning("Evento '%s' não publicado (broker indisponível?): %s", event, error)
