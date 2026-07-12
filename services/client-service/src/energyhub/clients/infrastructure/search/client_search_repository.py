"""Repositório de busca do cliente (Elasticsearch) — Fase 11.

Indexa (`save`), remove (`delete`) e roda _finders_ estruturados (`term`/`match`/`bool`) mantendo o
índice `clients` sincronizado com o Postgres (fonte de verdade). Construído com um cliente do
`ElasticsearchConfig`; `new_search()` abre uma `Search` no índice, tipada como `ClientDocument`.
"""

from __future__ import annotations

from uuid import UUID

from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch_dsl import Q, Search

from energyhub.clients.infrastructure.search.client_document import ClientDocument


class ClientSearchRepository:
    """Indexação + _finders_ estruturados do índice `clients`."""

    def __init__(self, client: Elasticsearch) -> None:
        self._client = client

    def new_search(self) -> Search:
        """Nova `Search` ligada ao cliente e ao índice `clients` (hits tipados `ClientDocument`)."""
        return ClientDocument.search(using=self._client)

    def save(self, document: ClientDocument) -> None:
        """Indexa (upsert por `meta.id`) o documento no índice `clients`."""
        document.save(using=self._client)

    def delete(self, doc_id: str | UUID) -> None:
        """Remove o documento por id (no-op se já não existir)."""
        try:
            self._client.delete(index=ClientDocument.Index.name, id=str(doc_id))
        except NotFoundError:
            pass

    def find_by_corporate_name_containing(self, name: str) -> list[ClientDocument]:
        """`match` na razão social (texto analisado em português)."""
        return list(self.new_search().query("match", corporate_name=name).execute())

    def find_by_city_and_state(self, city: str, state: str) -> list[ClientDocument]:
        """`term` combinado em `city` E `state` (campos keyword, casamento exato)."""
        response = (
            self.new_search()
            .query("bool", filter=[Q("term", city=city), Q("term", state=state)])
            .execute()
        )
        return list(response)

    def find_by_active_true(self) -> list[ClientDocument]:
        """Somente documentos com `active = true`."""
        return list(self.new_search().query("term", active=True).execute())
