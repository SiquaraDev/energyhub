"""Implementação base de repositório com SQLAlchemy async."""

from typing import Generic, TypeVar

from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.shared.domain.repository.repository import Repository

T = TypeVar("T")
ID = TypeVar("ID")


class SQLAlchemyRepository(Repository[T, ID], Generic[T, ID]):
    """CRUD genérico sobre uma sessão async do SQLAlchemy.

    Assume que `model_class` é um modelo ORM com uma coluna `id`. A tipagem
    completa de `id` será refinada quando a Base declarativa existir (Fase 4).
    """

    def __init__(self, session: AsyncSession, model_class: type[T]) -> None:
        self._session = session
        self._model_class = model_class

    async def save(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.commit()
        await self._session.refresh(entity)
        return entity

    async def find_by_id(self, entity_id: ID) -> T | None:
        result = await self._session.execute(
            select(self._model_class).where(self._model_class.id == entity_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def find_all(self) -> list[T]:
        result = await self._session.execute(select(self._model_class))
        return list(result.scalars().all())

    async def delete_by_id(self, entity_id: ID) -> None:
        await self._session.execute(
            delete(self._model_class).where(self._model_class.id == entity_id)  # type: ignore[attr-defined]
        )
        await self._session.commit()

    async def exists_by_id(self, entity_id: ID) -> bool:
        result = await self._session.execute(
            select(exists().where(self._model_class.id == entity_id))  # type: ignore[attr-defined]
        )
        return bool(result.scalar())
