"""Mapeamento imperativo do **contract-service** (Fase 15).

Dono **apenas** de `contracts` (banco `contractdb`). `client_id` é um **UUID simples** (sem FK) — a
tabela `clients` pertence ao client-service; a integridade referencial cross-context, quando
necessária, é verificada via `ClientClient` (HTTP), não por FK de banco.
"""

from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Numeric, String, Table, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import configure_mappers

from energyhub.contracts.domain.entity.contract import Contract
from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.domain.entity.contract_type import ContractType
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


contracts_table = Table(
    "contracts",
    metadata,
    _pk(),
    Column("contract_number", String(50), nullable=False, unique=True),
    Column("client_id", UUID(as_uuid=True), nullable=False),  # UUID simples (sem FK cross-context)
    Column("start_date", Date, nullable=False),
    Column("end_date", Date, nullable=False),
    Column("energy_amount", Numeric(18, 6), nullable=False),
    Column("unit_price", Numeric(18, 6), nullable=False),
    Column("total_value", Numeric(18, 2), nullable=False),
    Column("type", _enum(ContractType, 20), nullable=False),
    Column("status", _enum(ContractStatus, 20), server_default=text("'DRAFT'"), nullable=False),
    *_timestamps(),
)


_configured = False


def configure_mappings() -> None:
    """Registra o mapper imperativo de contratos (idempotente)."""
    global _configured
    if _configured:
        return
    registry.map_imperatively(Contract, contracts_table)
    configure_mappers()
    _configured = True
