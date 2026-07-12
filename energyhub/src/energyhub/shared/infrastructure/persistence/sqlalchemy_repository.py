"""Implementação base de repositório com SQLAlchemy async (mapeamento imperativo)."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import and_, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.shared.domain.repository.repository import Repository

T = TypeVar("T")
ID = TypeVar("ID")


class SQLAlchemyRepository(Repository[T, ID], Generic[T, ID]):
    """CRUD assíncrono genérico sobre uma `AsyncSession`, para qualquer entidade mapeada.

    `save` faz `add` + `flush` (populando o `id` gerado), mas **não** faz `commit`: a
    fronteira transacional pertence ao caller/use-case (a sessão por requisição). Com
    `expire_on_commit=False` na fábrica de sessões, os atributos seguem acessíveis após o
    commit externo.
    """

    def __init__(self, session: AsyncSession, entity_type: type[T]) -> None:
        self._session = session
        self._entity_type = entity_type

    async def save(self, entity: T) -> T:
        """Adiciona a entidade e faz flush para popular o `id`; retorna a própria entidade."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def find_by_id(self, entity_id: ID) -> T | None:
        """Busca pela chave primária (usa o identity map); retorna a entidade ou `None`."""
        return await self._session.get(self._entity_type, entity_id)

    async def find_all(self) -> list[T]:
        """Retorna todas as entidades (uso interno/conjuntos pequenos; prefira paginação)."""
        result = await self._session.execute(select(self._entity_type))
        return list(result.scalars().all())

    async def delete_by_id(self, entity_id: ID) -> None:
        """Remove a entidade pelo id, se existir (hard delete)."""
        entity = await self._session.get(self._entity_type, entity_id)
        if entity is not None:
            await self._session.delete(entity)
            await self._session.flush()

    async def exists_by_id(self, entity_id: ID) -> bool:
        """Indica se existe uma entidade com o id informado."""
        result = await self._session.execute(
            select(exists().where(self._entity_type.id == entity_id))  # type: ignore[attr-defined]
        )
        return bool(result.scalar())

    async def find_by(self, *conditions: Any) -> list[T]:
        """Consulta com condições SQLAlchemy compostas (ex.: vindas de um `*Filter`)."""
        stmt = select(self._entity_type)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_page(self, offset: int, limit: int, *conditions: Any) -> tuple[list[T], int]:
        """Retorna `(conteúdo da página, total de elementos)` aplicando offset/limit + count.

        A montagem do `PageResponse` (camada de aplicação) fica com o caller/use-case, para
        que a infraestrutura não dependa da aplicação (regra de dependência).
        """
        clause = and_(*conditions) if conditions else None
        count_stmt = select(func.count()).select_from(self._entity_type)
        list_stmt = select(self._entity_type)
        if clause is not None:
            count_stmt = count_stmt.where(clause)
            list_stmt = list_stmt.where(clause)
        total = (await self._session.execute(count_stmt)).scalar() or 0
        result = await self._session.execute(list_stmt.offset(offset).limit(limit))
        return list(result.scalars().all()), int(total)
