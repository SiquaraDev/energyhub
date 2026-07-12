"""Documento de busca do contrato (elasticsearch-dsl) — Fase 11.

Projeção denormalizada do `Contract` para o índice `contracts`: identificadores/status/tipo como
`Keyword`, datas como `Date` e o valor total como `Double`. `from_entity` achata enums em strings,
converte `Decimal` → `float` e o id → string (em `meta.id`).
"""

from __future__ import annotations

from elasticsearch_dsl import Date, Document, Double, Keyword

from energyhub.contracts.domain.entity.contract import Contract


class ContractDocument(Document):
    """Mapeamento de busca do contrato (índice `contracts`)."""

    contract_number = Keyword()
    client_id = Keyword()
    status = Keyword()
    type = Keyword()
    start_date = Date()
    end_date = Date()
    total_value = Double()

    class Index:
        name = "contracts"

    @classmethod
    def from_entity(cls, contract: Contract) -> ContractDocument:
        """Projeta um `Contract` de domínio no documento de busca (id em `meta.id`)."""
        document = cls(
            contract_number=contract.contract_number,
            client_id=str(contract.client_id),
            status=contract.status.value,
            type=contract.type.value,
            start_date=contract.start_date,
            end_date=contract.end_date,
            total_value=float(contract.total_value),
        )
        document.meta.id = str(contract.id)
        return document
