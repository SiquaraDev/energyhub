"""Exceção: relatório não encontrado."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class ReportNotFoundException(ResourceNotFoundException):
    """Lançada quando um relatório solicitado não existe (→ HTTP 404)."""

    error_code: ClassVar[str] = "REPORT_NOT_FOUND"
