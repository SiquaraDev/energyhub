"""Exceção: relatório não encontrado."""

from __future__ import annotations

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class ReportNotFoundException(ResourceNotFoundException):
    """Lançada quando um relatório solicitado não existe (→ HTTP 404)."""
