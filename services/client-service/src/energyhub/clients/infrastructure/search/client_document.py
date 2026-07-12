"""Documento de busca do cliente (elasticsearch-dsl) — Fase 11.

Projeção **denormalizada** e tipada do `Client` para o índice `clients`: atributos de filtro exato
como `Keyword` e os nomes (razão social/fantasia) como `Text` analisado em **português**.
`from_entity` converte a entidade de domínio em documento (id → string via `meta.id`).
"""

from __future__ import annotations

from elasticsearch_dsl import Boolean, Date, Document, Keyword, Text

from energyhub.clients.domain.entity.client import Client
from energyhub.shared.infrastructure.search.analyzers import portuguese_analyzer


class ClientDocument(Document):
    """Mapeamento de busca do cliente (índice `clients`)."""

    cnpj = Keyword()
    corporate_name = Text(analyzer=portuguese_analyzer)
    trade_name = Text(analyzer=portuguese_analyzer)
    email = Keyword()
    phone = Keyword()
    address = Keyword()
    city = Keyword()
    state = Keyword()
    zip_code = Keyword()
    active = Boolean()
    created_at = Date()
    updated_at = Date()

    class Index:
        name = "clients"

    @classmethod
    def from_entity(cls, client: Client) -> ClientDocument:
        """Projeta um `Client` de domínio no documento de busca (id em `meta.id`)."""
        document = cls(
            cnpj=client.cnpj,
            corporate_name=client.corporate_name,
            trade_name=client.trade_name,
            email=client.email,
            phone=client.phone,
            address=client.address,
            city=client.city,
            state=client.state,
            zip_code=client.zip_code,
            active=client.active,
            created_at=client.created_at,
            updated_at=client.updated_at,
        )
        document.meta.id = str(client.id)
        return document
