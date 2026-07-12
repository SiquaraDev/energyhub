"""Interface de repositório genérica do domínio (porta de persistência)."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class Repository(ABC, Generic[T, ID]):
    """Contrato de persistência independente de infraestrutura (CRUD genérico)."""

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Persiste (cria ou atualiza) a entidade e a retorna."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, entity_id: ID) -> T | None:
        """Retorna a entidade pelo identificador, ou None se não existir."""
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> list[T]:
        """Retorna todas as entidades."""
        raise NotImplementedError

    @abstractmethod
    async def delete_by_id(self, entity_id: ID) -> None:
        """Remove a entidade pelo identificador."""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_id(self, entity_id: ID) -> bool:
        """Indica se existe uma entidade com o identificador informado."""
        raise NotImplementedError
