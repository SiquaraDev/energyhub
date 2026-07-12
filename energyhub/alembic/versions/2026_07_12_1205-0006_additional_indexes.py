"""create additional indexes (composite and time-ordered)

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-12 12:05:00.000000+00:00

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Índices compostos para padrões de consulta multi-coluna e por faixa de datas.
    op.create_index("ix_contracts_client_id_status", "contracts", ["client_id", "status"])
    op.create_index("ix_contracts_start_date_end_date", "contracts", ["start_date", "end_date"])

    # Índices temporais para consultas cronológicas em logs/notificações.
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("ix_contracts_start_date_end_date", table_name="contracts")
    op.drop_index("ix_contracts_client_id_status", table_name="contracts")
