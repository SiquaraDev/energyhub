"""Mapeamento imperativo do **audit-service** (Fase 15).

Dono de `audit_logs` (banco `auditdb`). `user_id` é um **UUID simples** (sem FK — a tabela `users`
pertence ao auth-service). Trilha append-only alimentada pelo consumidor de eventos.
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String, Table, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import configure_mappers

from energyhub.audit.domain.entity.audit_action import AuditAction
from energyhub.audit.domain.entity.audit_log import AuditLog
from energyhub.shared.infrastructure.persistence.database import Base

metadata = Base.metadata
registry = Base.registry


def _pk() -> Column:
    return Column(
        "id", UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )


def _timestamps() -> list[Column]:
    return [
        Column(
            "created_at",
            DateTime(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        Column(
            "updated_at",
            DateTime(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    ]


audit_logs_table = Table(
    "audit_logs",
    metadata,
    _pk(),
    Column("user_id", UUID(as_uuid=True), nullable=False),  # UUID simples (sem FK cross-context)
    Column(
        "action",
        SAEnum(
            AuditAction,
            native_enum=False,
            length=20,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    ),
    Column("entity_type", String(100), nullable=False),
    Column("entity_id", UUID(as_uuid=True), nullable=False),
    Column("details", JSONB, server_default=text("'{}'::jsonb"), nullable=False),
    Column(
        "timestamp",
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    ),
    *_timestamps(),
)


_configured = False


def configure_mappings() -> None:
    """Registra o mapper imperativo de audit_logs (idempotente)."""
    global _configured
    if _configured:
        return
    registry.map_imperatively(AuditLog, audit_logs_table)
    configure_mappers()
    _configured = True
