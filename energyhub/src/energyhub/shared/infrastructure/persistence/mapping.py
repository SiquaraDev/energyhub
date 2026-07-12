"""Mapeamento imperativo (_classical mapping_) das entidades de domínio às tabelas da Fase 4.

As entidades permanecem _dataclasses_ puras — **sem** importar SQLAlchemy no domínio. As `Table`s e
os mappers vivem aqui, na infraestrutura, preservando a regra de dependência da Clean Architecture.
Os repositorios consultam as entidades diretamente (`select(User)...`): o mapper as instrumenta.

O schema físico é da Fase 4 (fonte de verdade); estas `Table`s são reconciliadas a ele — sem
`--autogenerate`. Chame `configure_mappings()` no startup (e nos testes) para registrar e validar
os mappers uma única vez.
"""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Table,
    Text,
    text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import configure_mappers, relationship

from energyhub.audit.domain.entity.audit_action import AuditAction
from energyhub.audit.domain.entity.audit_log import AuditLog
from energyhub.auth.domain.entity.permission import Permission
from energyhub.auth.domain.entity.role import Role
from energyhub.auth.domain.entity.user import User
from energyhub.clients.domain.entity.client import Client
from energyhub.clients.domain.entity.contact import Contact
from energyhub.clients.domain.entity.contact_type import ContactType
from energyhub.contracts.domain.entity.contract import Contract
from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.domain.entity.contract_type import ContractType
from energyhub.financial.domain.entity.invoice import Invoice
from energyhub.financial.domain.entity.invoice_status import InvoiceStatus
from energyhub.financial.domain.entity.payment import Payment
from energyhub.negotiations.domain.entity.energy_transaction import EnergyTransaction
from energyhub.negotiations.domain.entity.negotiation import Negotiation
from energyhub.negotiations.domain.entity.negotiation_status import NegotiationStatus
from energyhub.negotiations.domain.entity.transaction_type import TransactionType
from energyhub.notifications.domain.entity.notification import Notification
from energyhub.notifications.domain.entity.notification_status import NotificationStatus
from energyhub.reports.domain.entity.report import Report
from energyhub.shared.infrastructure.persistence.database import Base

metadata = Base.metadata
registry = Base.registry


def _pk() -> Column:
    return Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
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
    """Coluna de enum armazenada como VARCHAR (native_enum=False), guardando `.value`."""
    return SAEnum(
        enum_cls,
        native_enum=False,
        length=length,
        values_callable=lambda e: [member.value for member in e],
    )


# --- Tabelas (espelham as migrações da Fase 4) -------------------------------

users_table = Table(
    "users",
    metadata,
    _pk(),
    Column("username", String(150), nullable=False, unique=True),
    Column("password", String(255), nullable=False),
    Column("email", String(255), nullable=False, unique=True),
    Column("full_name", String(255)),
    Column("active", Boolean, server_default=text("true"), nullable=False),
    *_timestamps(),
)

roles_table = Table(
    "roles",
    metadata,
    _pk(),
    Column("name", String(100), nullable=False, unique=True),
    Column("description", String(255)),
    *_timestamps(),
)

permissions_table = Table(
    "permissions",
    metadata,
    _pk(),
    Column("name", String(100), nullable=False, unique=True),
    Column("description", String(255)),
    *_timestamps(),
)

user_roles_table = Table(
    "user_roles",
    metadata,
    Column(
        "user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
)

role_permissions_table = Table(
    "role_permissions",
    metadata,
    Column(
        "role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
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
        "client_id",
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("name", String(255), nullable=False),
    Column("type", _enum(ContactType, 20), nullable=False),
    Column("email", String(255)),
    Column("phone", String(20)),
    Column("position", String(100)),
    *_timestamps(),
)

contracts_table = Table(
    "contracts",
    metadata,
    _pk(),
    Column("contract_number", String(50), nullable=False, unique=True),
    Column(
        "client_id",
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("start_date", Date, nullable=False),
    Column("end_date", Date, nullable=False),
    Column("energy_amount", Numeric(18, 6), nullable=False),
    Column("unit_price", Numeric(18, 6), nullable=False),
    Column("total_value", Numeric(18, 2), nullable=False),
    Column("type", _enum(ContractType, 20), nullable=False),
    Column("status", _enum(ContractStatus, 20), server_default=text("'DRAFT'"), nullable=False),
    *_timestamps(),
)

negotiations_table = Table(
    "negotiations",
    metadata,
    _pk(),
    Column(
        "contract_id",
        UUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("status", _enum(NegotiationStatus, 20), server_default=text("'DRAFT'"), nullable=False),
    *_timestamps(),
)

energy_transactions_table = Table(
    "energy_transactions",
    metadata,
    _pk(),
    Column(
        "negotiation_id",
        UUID(as_uuid=True),
        ForeignKey("negotiations.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("amount", Numeric(18, 6), nullable=False),
    Column("price", Numeric(18, 6), nullable=False),
    Column("type", _enum(TransactionType, 10), nullable=False),
    Column("transaction_date", DateTime(timezone=True), nullable=False),
    *_timestamps(),
)

invoices_table = Table(
    "invoices",
    metadata,
    _pk(),
    Column("invoice_number", String(50), nullable=False, unique=True),
    Column(
        "client_id",
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="RESTRICT"),
        nullable=False,
    ),
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

audit_logs_table = Table(
    "audit_logs",
    metadata,
    _pk(),
    Column(
        "user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    ),
    Column("action", _enum(AuditAction, 20), nullable=False),
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

notifications_table = Table(
    "notifications",
    metadata,
    _pk(),
    Column(
        "user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    ),
    Column("title", String(255), nullable=False),
    Column("message", Text, nullable=False),
    Column(
        "status", _enum(NotificationStatus, 20), server_default=text("'PENDING'"), nullable=False
    ),
    *_timestamps(),
)

reports_table = Table(
    "reports",
    metadata,
    _pk(),
    Column("report_type", String(100), nullable=False),
    Column(
        "generated_by",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("parameters", JSONB, server_default=text("'{}'::jsonb"), nullable=False),
    Column("file_path", String(500)),
    Column("status", String(50), server_default=text("'PENDING'"), nullable=False),
    *_timestamps(),
)


_configured = False


def configure_mappings() -> None:
    """Registra os mappers imperativos e resolve os relacionamentos (idempotente)."""
    global _configured
    if _configured:
        return

    registry.map_imperatively(Permission, permissions_table)
    registry.map_imperatively(
        Role,
        roles_table,
        properties={
            "permissions": relationship(Permission, secondary=role_permissions_table),
            "users": relationship(User, secondary=user_roles_table, back_populates="roles"),
        },
    )
    registry.map_imperatively(
        User,
        users_table,
        properties={
            "roles": relationship(Role, secondary=user_roles_table, back_populates="users"),
        },
    )
    registry.map_imperatively(
        Client,
        clients_table,
        properties={"contacts": relationship(Contact, back_populates="client")},
    )
    registry.map_imperatively(
        Contact,
        contacts_table,
        properties={"client": relationship(Client, back_populates="contacts")},
    )
    registry.map_imperatively(
        Contract, contracts_table, properties={"client": relationship(Client)}
    )
    registry.map_imperatively(
        Negotiation, negotiations_table, properties={"contract": relationship(Contract)}
    )
    registry.map_imperatively(
        EnergyTransaction,
        energy_transactions_table,
        properties={"negotiation": relationship(Negotiation)},
    )
    registry.map_imperatively(Invoice, invoices_table, properties={"client": relationship(Client)})
    registry.map_imperatively(
        Payment, payments_table, properties={"invoice": relationship(Invoice)}
    )
    registry.map_imperatively(AuditLog, audit_logs_table, properties={"user": relationship(User)})
    registry.map_imperatively(
        Notification, notifications_table, properties={"user": relationship(User)}
    )
    registry.map_imperatively(Report, reports_table)

    configure_mappers()
    _configured = True
