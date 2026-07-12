"""Mapeamento imperativo do **client-service** (Fase 15).

Dono **apenas** de `clients` e `contacts`. Não mapeia entidades de outros contextos — o serviço
possui seu próprio banco (`clientdb`) e nunca lê as tabelas de outro serviço.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import configure_mappers, relationship

from energyhub.clients.domain.entity.client import Client
from energyhub.clients.domain.entity.contact import Contact
from energyhub.clients.domain.entity.contact_type import ContactType
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


clients_table = Table(
    "clients",
    metadata,
    _pk(),
    Column("cnpj", String(18), nullable=False, unique=True),
    Column("corporate_name", String(255), nullable=False),
    Column("trade_name", String(255)),
    Column("email", String(255)),
    Column("phone", String(20)),
    Column("address", String(255)),
    Column("city", String(100)),
    Column("state", String(100)),
    Column("zip_code", String(20)),
    Column("active", Boolean, server_default=text("true"), nullable=False),
    *_timestamps(),
)

contacts_table = Table(
    "contacts",
    metadata,
    _pk(),
    Column(
        "client_id", UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    ),
    Column("name", String(255), nullable=False),
    Column("type", _enum(ContactType, 20), nullable=False),
    Column("email", String(255)),
    Column("phone", String(20)),
    Column("position", String(100)),
    *_timestamps(),
)


_configured = False


def configure_mappings() -> None:
    """Registra os mappers imperativos de clientes/contatos (idempotente)."""
    global _configured
    if _configured:
        return

    registry.map_imperatively(
        Client,
        clients_table,
        properties={"contacts": relationship(Contact, lazy="selectin", viewonly=True)},
    )
    registry.map_imperatively(Contact, contacts_table)

    configure_mappers()
    _configured = True
