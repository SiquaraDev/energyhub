"""Testes unitários de `publish_safely` (efeito colateral não-bloqueante)."""

from __future__ import annotations

import pytest

from energyhub.shared.domain.exception.message_publishing_exception import (
    MessagePublishingException,
)
from energyhub.shared.infrastructure.messaging.publish_helper import publish_safely


async def _ok() -> None:
    return None


async def _raises_publishing() -> None:
    raise MessagePublishingException("broker fora do ar")


async def _raises_other() -> None:
    raise RuntimeError("erro inesperado")


async def test_publish_safely_swallows_publishing_exception() -> None:
    # Uma falha de broker é logada, não propaga (a escrita de negócio não é desfeita).
    await publish_safely(_raises_publishing(), event="client.created")


async def test_publish_safely_passes_through_on_success() -> None:
    await publish_safely(_ok(), event="client.created")


async def test_publish_safely_reraises_unexpected_errors() -> None:
    with pytest.raises(RuntimeError):
        await publish_safely(_raises_other(), event="client.created")
