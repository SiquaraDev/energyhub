"""Repositório de busca do contrato (Elasticsearch) — Fase 11.

Indexa (`save`), remove (`delete`) e roda _finders_ estruturados sobre o índice `contracts`.
Análogo ao `ClientSearchRepository`; mantém o índice sincronizado com o Postgres (fonte de verdade).
"""

from __future__ import annotations

from uuid import UUID

from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch_dsl import Search

from energyhub.contracts.infrastructure.search.contract_document import ContractDocument


class ContractSearchRepository:
    """Indexação + _finders_ estruturados do índice `contracts`."""

    def __init__(self, client: Elasticsearch) -> None:
        self._client = client

    def new_search(self) -> Search:
        """Nova `Search` ligada ao cliente e ao índice `contracts`."""
        return ContractDocument.search(using=self._client)

    def save(self, document: ContractDocument) -> None:
        """Indexa (upsert por `meta.id`) o documento no índice `contracts`."""
        document.save(using=self._client)

    def delete(self, doc_id: str | UUID) -> None:
        """Remove o documento por id (no-op se já não existir)."""
        try:
            self._client.delete(index=ContractDocument.Index.name, id=str(doc_id))
        except NotFoundError:
            pass

    def find_by_status(self, status: str) -> list[ContractDocument]:
        """`term` no status (keyword)."""
        return list(self.new_search().query("term", status=status).execute())

    def find_by_client_id(self, client_id: str | UUID) -> list[ContractDocument]:
        """`term` no `client_id` (keyword) — contratos de um cliente."""
        return list(self.new_search().query("term", client_id=str(client_id)).execute())

    def find_by_type(self, contract_type: str) -> list[ContractDocument]:
        """`term` no tipo (keyword)."""
        return list(self.new_search().query("term", type=contract_type).execute())
