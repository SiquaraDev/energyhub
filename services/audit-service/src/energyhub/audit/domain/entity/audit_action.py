from __future__ import annotations

from enum import Enum


class AuditAction(str, Enum):
    """Ações auditáveis registradas no log de auditoria."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
