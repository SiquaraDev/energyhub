"""create constraints and updated_at triggers

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-12 12:06:00.000000+00:00

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Tabelas que possuem coluna `updated_at` e recebem o trigger de manutenção.
_TABLES_WITH_UPDATED_AT: tuple[str, ...] = (
    "users",
    "roles",
    "permissions",
    "clients",
    "contacts",
    "contracts",
    "negotiations",
    "energy_transactions",
    "invoices",
    "payments",
    "audit_logs",
    "notifications",
    "reports",
)


def upgrade() -> None:
    # --- CHECK constraints (invariantes de domínio no nível do banco) --------
    # E-mail em formato válido (consistente com a validação do domínio).
    op.create_check_constraint(
        "ck_users_email_format",
        "users",
        r"email ~* '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'",
    )
    # CNPJ formatado (XX.XXX.XXX/XXXX-XX) ou 14 dígitos.
    op.create_check_constraint(
        "ck_clients_cnpj_format",
        "clients",
        r"cnpj ~ '^[0-9]{14}$' OR cnpj ~ '^[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2}$'",
    )
    # Ordenação de datas do contrato.
    op.create_check_constraint(
        "ck_contracts_date_order",
        "contracts",
        "end_date > start_date",
    )
    # Valores monetários/quantidades positivos.
    op.create_check_constraint(
        "ck_contracts_positive_amounts",
        "contracts",
        "energy_amount > 0 AND unit_price > 0 AND total_value > 0",
    )

    # --- Função + triggers de manutenção de `updated_at` ---------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)
    for table in _TABLES_WITH_UPDATED_AT:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
            """)


def downgrade() -> None:
    # Remove triggers, depois a função, depois as CHECK constraints.
    for table in _TABLES_WITH_UPDATED_AT:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    op.drop_constraint("ck_contracts_positive_amounts", "contracts", type_="check")
    op.drop_constraint("ck_contracts_date_order", "contracts", type_="check")
    op.drop_constraint("ck_clients_cnpj_format", "clients", type_="check")
    op.drop_constraint("ck_users_email_format", "users", type_="check")
