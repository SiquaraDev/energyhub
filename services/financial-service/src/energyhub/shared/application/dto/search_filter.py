"""DTOs de filtro de busca avançada (Fase 11).

`SearchFilter` carrega uma consulta textual opcional, os campos-alvo, a fuzziness, um score mínimo e
uma lista de `FilterCondition` (campo + operador + valor). O serviço as traduz numa query `bool`
composta (ver `advanced_search`).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

FilterOperator = Literal["eq", "gt", "lt", "gte", "lte"]


class FilterCondition(BaseModel):
    """Uma condição de filtro: `field` `operator` `value` (ex.: `total_value gte 1000`)."""

    field: str = Field(description="Campo do documento a filtrar", examples=["state"])
    operator: FilterOperator = Field(
        description="Operador: eq (term) ou gt/lt/gte/lte (range)", examples=["eq"]
    )
    value: str | int | float | bool = Field(description="Valor de comparação", examples=["SP"])


class SearchFilter(BaseModel):
    """Critérios de busca avançada — todos opcionais; campos ausentes não geram cláusulas."""

    query: str | None = Field(default=None, description="Texto livre (multi_match opcional)")
    fields: list[str] = Field(
        default_factory=list,
        description="Campos-alvo do texto (com boosting, ex.: 'corporate_name^2')",
    )
    fuzzy: bool = Field(default=True, description="Habilita fuzziness='AUTO' no multi_match")
    min_score: float | None = Field(default=None, description="Score mínimo (exclui abaixo dele)")
    conditions: list[FilterCondition] = Field(
        default_factory=list, description="Condições de filtro (term/range)"
    )
