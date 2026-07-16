"""Ator corrente da requisição (change `fix-microservices-gaps`).

`AuditEvent.user_id` é obrigatório, mas os serviços de aplicação não recebem o usuário autenticado
por parâmetro: os routers usam `get_current_user` apenas como GUARD (`dependencies=[...]`), sem
ligá-lo a uma variável. Em vez de propagar um novo parâmetro por todas as camadas (rejeitado no
design), o `get_current_user` publica o id do ator num ContextVar — isolado por requisição/task no
asyncio — e os serviços o leem ao montar o evento de auditoria. Escritas sem usuário autenticado em
escopo (ex.: iniciadas pelo sistema) usam o sentinela abaixo, mantendo o contrato válido.
"""

from __future__ import annotations

from contextvars import ContextVar
from uuid import UUID

#: Ator sentinela para escritas iniciadas pelo sistema (sem usuário autenticado em escopo).
SYSTEM_ACTOR_ID = UUID("00000000-0000-0000-0000-000000000000")

_current_actor: ContextVar[UUID | None] = ContextVar("current_actor", default=None)


def set_current_actor(actor_id: UUID | None) -> None:
    """Publica o id do ator autenticado no contexto da requisição."""
    _current_actor.set(actor_id)


def get_current_actor() -> UUID:
    """Id do ator corrente; `SYSTEM_ACTOR_ID` quando não há usuário autenticado em escopo."""
    return _current_actor.get() or SYSTEM_ACTOR_ID
