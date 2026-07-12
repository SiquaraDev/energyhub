"""Mapeamento imperativo do **financial-service** (Fase 15).

Dono de `invoices` e `payments` (banco `financialdb`). `invoices.client_id` é um **UUID simples**
(sem FK — a tabela `clients` pertence ao client-service). A FK `payments.invoice_id → invoices` é
interna ao serviço e é mantida.
"""

from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, ForeignKey, Numeric, String, Table, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import configure_mappers

from energyhub.financial.domain.entity.invoice import Invoice
from energyhub.financial.domain.entity.invoice_status import InvoiceStatus
from energyhub.financial.domain.entity.payment import Payment
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


def _enum(enum_cls: type, length: int) -> SAEnum:
    return SAEnum(
        enum_cls,
        native_enum=False,
        length=length,
        values_callable=lambda e: [member.value for member in e],
    )


invoices_table = Table(
    "invoices",
    metadata,
    _pk(),
    Column("invoice_number", String(50), nullable=False, unique=True),
    Column("client_id", UUID(as_uuid=True), nullable=False),  # UUID simples (sem FK cross-context)
    Column("amount", Numeric(18, 2), nullable=False),
    Column("due_date", Date, nullable=False),
    Column("status", _enum(InvoiceStatus, 20), server_default=text("'DRAFT'"), nullable=False),
    *_timestamps(),
)

payments_table = Table(
    "payments",
    metadata,
    _pk(),
    Column(
        "invoice_id",
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("amount", Numeric(18, 2), nullable=False),
    Column("payment_date", DateTime(timezone=True), nullable=False),
    *_timestamps(),
)


_configured = False


def configure_mappings() -> None:
    """Registra os mappers imperativos de faturas/pagamentos (idempotente)."""
    global _configured
    if _configured:
        return
    registry.map_imperatively(Invoice, invoices_table)
    registry.map_imperatively(Payment, payments_table)
    configure_mappers()
    _configured = True
