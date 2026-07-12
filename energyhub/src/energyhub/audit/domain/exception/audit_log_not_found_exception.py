"""Exceção: log de auditoria não encontrado."""

from __future__ import annotations

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class AuditLogNotFoundException(ResourceNotFoundException):
    """Lançada quando um log de auditoria solicitado não existe (→ HTTP 404)."""
