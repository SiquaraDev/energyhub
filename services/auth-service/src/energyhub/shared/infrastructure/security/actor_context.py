"""Ator corrente da requisicao (change `fix-microservices-gaps`).

`AuditEvent.user_id` e obrigatorio, mas os servicos de aplicacao nao recebem o usuario autenticado
por parametro: os routers usam `get_current_user` apenas como GUARD (`dependencies=[...]`), sem
liga-lo a uma variavel. Em vez de propagar um novo parametro por todas as camadas (rejeitado no
design), o `get_current_user` publica o id do ator num ContextVar — isolado por requisicao/task no
asyncio — e os servicos o leem ao montar o evento de auditoria. Escritas sem usuario autenticado em
escopo (ex.: iniciadas pelo sistema) usam o sentinela abaixo, mantendo o contrato valido.
"""

from __future__ import annotations

from contextvars import ContextVar
from uuid import UUID

#: Ator sentinela para escritas iniciadas pelo sistema (sem usuario autenticado em escopo).
SYSTEM_ACTOR_ID = UUID("00000000-0000-0000-0000-000000000000")

_current_actor: ContextVar[UUID | None] = ContextVar("current_actor", default=None)


def set_current_actor(actor_id: UUID | None) -> None:
    """Publica o id do ator autenticado no contexto da requisicao."""
    _current_actor.set(actor_id)


def get_current_actor() -> UUID:
    """Id do ator corrente; `SYSTEM_ACTOR_ID` quando nao ha usuario autenticado em escopo."""
    return _current_actor.get() or SYSTEM_ACTOR_ID
