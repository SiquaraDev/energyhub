from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from energyhub.shared.domain.entity.base_entity import BaseEntity
from energyhub.shared.domain.exception.validation_exception import ValidationException


@dataclass(kw_only=True, eq=False)
class Report(BaseEntity):
    """Relatório gerado sob demanda (raiz do ReportAggregate).

    `report_type` e `status` são strings livres (sem enum dedicado nesta fase).
    """

    report_type: str
    generated_by: UUID
    parameters: dict[str, Any] = field(default_factory=dict)
    file_path: str | None = None
    status: str = "PENDING"

    def __post_init__(self) -> None:
        """Valida os campos obrigatórios do relatório."""
        super().__post_init__()
        if not self.report_type or not self.report_type.strip():
            raise ValidationException("report_type não pode ser vazio")
        if not self.status or not self.status.strip():
            raise ValidationException("status não pode ser vazio")
