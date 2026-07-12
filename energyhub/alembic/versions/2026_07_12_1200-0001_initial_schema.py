"""initial schema (auth, clients, contracts)

Revision ID: 0001
Revises:
Create Date: 2026-07-12 12:00:00.000000+00:00

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# Identificadores de revisão usados pelo Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _uuid_pk() -> sa.Column:
    """Coluna de chave primária UUID com default `gen_random_uuid()`."""
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
        nullable=False,
    )


def _timestamps() -> list[sa.Column]:
    """Colunas `created_at`/`updated_at` (timezone-aware, default agora)."""
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    # Garante gen_random_uuid() em qualquer PostgreSQL (no-op no PG13+).
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # --- auth: users ---------------------------------------------------------
    op.create_table(
        "users",
        _uuid_pk(),
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # --- auth: roles ---------------------------------------------------------
    op.create_table(
        "roles",
        _uuid_pk(),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    # --- auth: permissions ---------------------------------------------------
    op.create_table(
        "permissions",
        _uuid_pk(),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_permissions_name", "permissions", ["name"], unique=True)

    # --- auth: user_roles (join) ---------------------------------------------
    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )

    # --- auth: role_permissions (join) ---------------------------------------
    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    # --- clients -------------------------------------------------------------
    op.create_table(
        "clients",
        _uuid_pk(),
        sa.Column("cnpj", sa.String(length=18), nullable=False),
        sa.Column("corporate_name", sa.String(length=255), nullable=False),
        sa.Column("trade_name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("zip_code", sa.String(length=20), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_clients_cnpj", "clients", ["cnpj"], unique=True)
    op.create_index("ix_clients_active", "clients", ["active"])

    # --- contacts ------------------------------------------------------------
    op.create_table(
        "contacts",
        _uuid_pk(),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("position", sa.String(length=100), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_contacts_client_id", "contacts", ["client_id"])
    op.create_index("ix_contacts_type", "contacts", ["type"])

    # --- contracts -----------------------------------------------------------
    op.create_table(
        "contracts",
        _uuid_pk(),
        sa.Column("contract_number", sa.String(length=50), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("energy_amount", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("total_value", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="DRAFT", nullable=False),
        *_timestamps(),
        # RESTRICT: contratos são registros de negócio e não devem sumir com o cliente.
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_contracts_contract_number", "contracts", ["contract_number"], unique=True)
    op.create_index("ix_contracts_client_id", "contracts", ["client_id"])
    op.create_index("ix_contracts_status", "contracts", ["status"])


def downgrade() -> None:
    # Ordem reversa de dependência; drop_table remove também os índices da tabela.
    op.drop_table("contracts")
    op.drop_table("contacts")
    op.drop_table("clients")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
