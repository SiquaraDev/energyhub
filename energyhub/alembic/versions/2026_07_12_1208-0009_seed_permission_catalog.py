"""seed full permission catalog and grant all permissions to ADMIN (Fase 7)

Revision ID: 0009
Revises: 0008
Create Date: 2026-07-12 12:08:00.000000+00:00

Complementa o seed da 0008 (que trazia apenas as permissões USER_*) com o catálogo completo de
permissões `<RECURSO>_<AÇÃO>` usado pelos guards RBAC da Fase 7, e concede **todas** as permissões
ao papel ADMIN. Os nomes são a fonte espelhada de `energyhub.shared.constant.permissions`.
"""

from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ROLE_ADMIN = "11111111-1111-1111-1111-111111111111"

# Novas permissões introduzidas nesta migração (USER_* já vieram na 0008).
# (uuid determinístico, nome, descrição)
_NEW_PERMISSIONS: list[tuple[str, str, str]] = [
    ("00000000-0000-0000-0000-000000000201", "ROLE_CREATE", "Criar papéis"),
    ("00000000-0000-0000-0000-000000000202", "ROLE_READ", "Ler papéis"),
    ("00000000-0000-0000-0000-000000000203", "ROLE_UPDATE", "Atualizar papéis"),
    ("00000000-0000-0000-0000-000000000204", "ROLE_DELETE", "Remover papéis"),
    ("00000000-0000-0000-0000-000000000301", "PERMISSION_CREATE", "Criar permissões"),
    ("00000000-0000-0000-0000-000000000302", "PERMISSION_READ", "Ler permissões"),
    ("00000000-0000-0000-0000-000000000303", "PERMISSION_UPDATE", "Atualizar permissões"),
    ("00000000-0000-0000-0000-000000000304", "PERMISSION_DELETE", "Remover permissões"),
    ("00000000-0000-0000-0000-000000000401", "CLIENT_CREATE", "Criar clientes"),
    ("00000000-0000-0000-0000-000000000402", "CLIENT_READ", "Ler clientes"),
    ("00000000-0000-0000-0000-000000000403", "CLIENT_UPDATE", "Atualizar clientes"),
    ("00000000-0000-0000-0000-000000000404", "CLIENT_DELETE", "Remover clientes"),
    ("00000000-0000-0000-0000-000000000501", "CONTRACT_CREATE", "Criar contratos"),
    ("00000000-0000-0000-0000-000000000502", "CONTRACT_READ", "Ler contratos"),
    ("00000000-0000-0000-0000-000000000503", "CONTRACT_UPDATE", "Atualizar contratos"),
    ("00000000-0000-0000-0000-000000000504", "CONTRACT_DELETE", "Remover contratos"),
    ("00000000-0000-0000-0000-000000000601", "NEGOTIATION_CREATE", "Criar negociações"),
    ("00000000-0000-0000-0000-000000000602", "NEGOTIATION_READ", "Ler negociações"),
    ("00000000-0000-0000-0000-000000000603", "NEGOTIATION_UPDATE", "Atualizar negociações"),
    ("00000000-0000-0000-0000-000000000604", "NEGOTIATION_DELETE", "Remover negociações"),
    ("00000000-0000-0000-0000-000000000701", "INVOICE_CREATE", "Criar faturas"),
    ("00000000-0000-0000-0000-000000000702", "INVOICE_READ", "Ler faturas"),
    ("00000000-0000-0000-0000-000000000703", "INVOICE_UPDATE", "Atualizar faturas"),
    ("00000000-0000-0000-0000-000000000704", "INVOICE_DELETE", "Remover faturas"),
    ("00000000-0000-0000-0000-000000000801", "AUDIT_LOG_CREATE", "Registrar logs de auditoria"),
    ("00000000-0000-0000-0000-000000000802", "AUDIT_LOG_READ", "Ler logs de auditoria"),
    ("00000000-0000-0000-0000-000000000901", "NOTIFICATION_CREATE", "Criar notificações"),
    ("00000000-0000-0000-0000-000000000902", "NOTIFICATION_READ", "Ler notificações"),
    ("00000000-0000-0000-0000-000000000903", "NOTIFICATION_UPDATE", "Atualizar notificações"),
    ("00000000-0000-0000-0000-000000000904", "NOTIFICATION_DELETE", "Remover notificações"),
    ("00000000-0000-0000-0000-000000000a01", "REPORT_CREATE", "Criar relatórios"),
    ("00000000-0000-0000-0000-000000000a02", "REPORT_READ", "Ler relatórios"),
    ("00000000-0000-0000-0000-000000000a03", "REPORT_UPDATE", "Atualizar relatórios"),
    ("00000000-0000-0000-0000-000000000a04", "REPORT_DELETE", "Remover relatórios"),
]


def upgrade() -> None:
    # Insere as novas permissões (idempotente).
    values = ",\n            ".join(
        f"('{pid}', '{name}', '{desc}')" for pid, name, desc in _NEW_PERMISSIONS
    )
    op.execute(f"""
        INSERT INTO permissions (id, name, description) VALUES
            {values}
        ON CONFLICT DO NOTHING;
        """)

    # Concede TODAS as permissões existentes ao papel ADMIN (idempotente e à prova de futuro:
    # qualquer permissão semeada — agora ou depois — passa a ser concedida ao ADMIN).
    op.execute(f"""
        INSERT INTO role_permissions (role_id, permission_id)
            SELECT '{ROLE_ADMIN}', id FROM permissions
        ON CONFLICT DO NOTHING;
        """)


def downgrade() -> None:
    # Remove apenas o que esta migração adicionou (as concessões USER_* da 0008 permanecem).
    ids = ", ".join(f"'{pid}'" for pid, _, _ in _NEW_PERMISSIONS)
    op.execute(
        f"DELETE FROM role_permissions WHERE role_id = '{ROLE_ADMIN}' "
        f"AND permission_id IN ({ids})"
    )
    op.execute(f"DELETE FROM permissions WHERE id IN ({ids})")
