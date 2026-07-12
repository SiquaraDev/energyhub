"""Configuração do Elasticsearch (Fase 11).

`ElasticsearchConfig.get_client()` é uma _factory_ do cliente síncrono (singleton reutilizável,
ligado a `settings.elasticsearch_url`/`elasticsearch_timeout`). `create_indices(documents)` cria
cada índice **apenas se ainda não existir** (idempotente — seguro re-executar no startup).

O Elasticsearch é um **índice de leitura denormalizado**: o Postgres segue a fonte de verdade e o
índice é reconstruível a qualquer momento a partir dele.

Alavancas de _tuning_ (quando a latência degradar, sem alterar o contrato de busca):
- adicionar campos `Keyword` para filtros/ordenações exatas frequentes (evita _fielddata_);
- ajustar o analisador (stopwords/stemming) dos campos `Text` para a distribuição real de termos;
- dimensionar _shards_/réplicas conforme o volume (dev single-node usa 1 shard / 0 réplicas).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from elasticsearch import Elasticsearch

from energyhub.config.settings import settings

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = logging.getLogger(__name__)


class ElasticsearchConfig:
    """Factory do cliente Elasticsearch + bootstrap idempotente de índices."""

    _client: Elasticsearch | None = None

    @classmethod
    def get_client(cls) -> Elasticsearch:
        """Retorna o cliente síncrono (singleton), ligado à URL/timeout das settings."""
        if cls._client is None:
            cls._client = Elasticsearch(
                hosts=[settings.elasticsearch_url],
                request_timeout=settings.elasticsearch_timeout,
            )
        return cls._client

    @classmethod
    def create_indices(cls, documents: Iterable[Any]) -> None:
        """Cria os índices dos `documents` que ainda não existem (idempotente).

        Recebe as classes `Document` do chamador (a composition root), preservando a regra de
        dependência — `shared` não importa os módulos de negócio.
        """
        client = cls.get_client()
        for document in documents:
            index_name = document.Index.name
            if not client.indices.exists(index=index_name):
                document.init(using=client)
                logger.info("Índice Elasticsearch criado: %s", index_name)
            else:
                logger.info("Índice Elasticsearch já existe: %s", index_name)
