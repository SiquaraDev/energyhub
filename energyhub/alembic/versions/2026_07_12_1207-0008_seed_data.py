"""insert initial data (roles, permissions, admin grants, admin user)

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-12 12:07:00.000000+00:00

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# UUIDs fixos e determinísticos (tornam grants e rollbacks referenciáveis).
ROLE_ADMIN = "11111111-1111-1111-1111-111111111111"
ROLE_OPERATOR = "22222222-2222-2222-2222-222222222222"
ROLE_CLIENT = "33333333-3333-3333-3333-333333333333"

PERM_USER_CREATE = "00000000-0000-0000-0000-000000000101"
PERM_USER_READ = "00000000-0000-0000-0000-000000000102"
PERM_USER_UPDATE = "00000000-0000-0000-0000-000000000103"
PERM_USER_DELETE = "00000000-0000-0000-0000-000000000104"
_PERMISSION_IDS = (PERM_USER_CREATE, PERM_USER_READ, PERM_USER_UPDATE, PERM_USER_DELETE)

ADMIN_USER = "00000000-0000-0000-0000-000000000001"

# Hash bcrypt (rounds=12) da senha "ChangeMe123!".
# ATENÇÃO: credencial de bootstrap NÃO-produtiva — DEVE ser rotacionada antes de deploy.
ADMIN_PASSWORD_HASH = "$2b$12$W7wqbZCKOFH06ar9tZKF/uyqc4C9atGAFzunNckGePhWWrRvmwyPG"


def upgrade() -> None:
    # Papéis padrão (idempotente).
    op.execute(f"""
        INSERT INTO roles (id, name, description) VALUES
            ('{ROLE_ADMIN}', 'ADMIN', 'Administrador do sistema'),
            ('{ROLE_OPERATOR}', 'OPERATOR', 'Operador'),
            ('{ROLE_CLIENT}', 'CLIENT', 'Cliente')
        ON CONFLICT DO NOTHING;
        """)

    # Permissões base (idempotente).
    op.execute(f"""
        INSERT INTO permissions (id, name, description) VALUES
            ('{PERM_USER_CREATE}', 'USER_CREATE', 'Criar usuários'),
            ('{PERM_USER_READ}', 'USER_READ', 'Ler usuários'),
            ('{PERM_USER_UPDATE}', 'USER_UPDATE', 'Atualizar usuários'),
            ('{PERM_USER_DELETE}', 'USER_DELETE', 'Remover usuários')
        ON CONFLICT DO NOTHING;
        """)

    # Concede todas as permissões seedadas ao papel ADMIN.
    values = ",\n            ".join(f"('{ROLE_ADMIN}', '{pid}')" for pid in _PERMISSION_IDS)
    op.execute(f"""
        INSERT INTO role_permissions (role_id, permission_id) VALUES
            {values}
        ON CONFLICT DO NOTHING;
        """)

    # Usuário admin padrão (idempotente).
    op.execute(f"""
        INSERT INTO users (id, username, password, email, full_name, active) VALUES
            ('{ADMIN_USER}', 'admin', '{ADMIN_PASSWORD_HASH}',
             'admin@energyhub.local', 'Administrador', true)
        ON CONFLICT DO NOTHING;
        """)

    # Vincula o admin ao papel ADMIN.
    op.execute(f"""
        INSERT INTO user_roles (user_id, role_id) VALUES
            ('{ADMIN_USER}', '{ROLE_ADMIN}')
        ON CONFLICT DO NOTHING;
        """)


def downgrade() -> None:
    # Remove exatamente as linhas seedadas, em ordem reversa de dependência.
    op.execute(
        f"DELETE FROM user_roles WHERE user_id = '{ADMIN_USER}' AND role_id = '{ROLE_ADMIN}'"
    )
    op.execute(f"DELETE FROM users WHERE id = '{ADMIN_USER}'")

    perm_list = ", ".join(f"'{pid}'" for pid in _PERMISSION_IDS)
    op.execute(
        f"DELETE FROM role_permissions WHERE role_id = '{ROLE_ADMIN}' "
        f"AND permission_id IN ({perm_list})"
    )
    op.execute(f"DELETE FROM permissions WHERE id IN ({perm_list})")
    op.execute(
        f"DELETE FROM roles WHERE id IN ('{ROLE_ADMIN}', '{ROLE_OPERATOR}', '{ROLE_CLIENT}')"
    )
