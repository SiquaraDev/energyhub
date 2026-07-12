"""negotiations and energy_transactions

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-12 12:01:00.000000+00:00

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _uuid_pk() -> sa.Column:
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
        nullable=False,
    )


def _timestamps() -> list[sa.Column]:
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
    op.create_table(
        "negotiations",
        _uuid_pk(),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="DRAFT", nullable=False),
        *_timestamps(),
        # RESTRICT: preserva o histórico do contrato associado.
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_negotiations_contract_id", "negotiations", ["contract_id"])

    op.create_table(
        "energy_transactions",
        _uuid_pk(),
        sa.Column("negotiation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("price", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("type", sa.String(length=10), nullable=False),
        sa.Column("transaction_date", sa.DateTime(timezone=True), nullable=False),
        *_timestamps(),
        # CASCADE: transações pertencem à negociação (filhas).
        sa.ForeignKeyConstraint(["negotiation_id"], ["negotiations.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_energy_transactions_negotiation_id", "energy_transactions", ["negotiation_id"]
    )


def downgrade() -> None:
    op.drop_table("energy_transactions")
    op.drop_table("negotiations")
