"""insert initial data (roles, permissions, admin grants, admin user)

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-12 12:07:00.000000+00:00

"""

import os
from collections.abc import Sequence
from typing import Union

import bcrypt  # o projeto usa bcrypt direto (passlib 1.7.4 é incompatível com bcrypt 5.x)
import sqlalchemy as sa

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


def _resolve_admin_hash() -> str | None:
    """Hash bcrypt do admin derivado de um SECRET de deploy (harden-security-credentials).

    Precedência: `ADMIN_PASSWORD_HASH` (hash pronto) → `ADMIN_PASSWORD` (texto, hasheado aqui).
    Retorna `None` se nenhum for fornecido — nesse caso o usuário admin **não** é semeado (nunca se
    usa uma senha publicada/commitada). Forneça a credencial via variável de ambiente/secret e rode
    a migração no deploy.
    """
    precomputed = os.environ.get("ADMIN_PASSWORD_HASH")
    if precomputed:
        return precomputed
    plaintext = os.environ.get("ADMIN_PASSWORD")
    if plaintext:
        return bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
    return None


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

    # Usuário admin padrão (idempotente). A senha vem de um SECRET de deploy (ADMIN_PASSWORD/
    # ADMIN_PASSWORD_HASH), nunca de um hash commitado. Sem credencial fornecida → admin não é
    # semeado (o vínculo com o papel também é pulado, pois depende da linha do usuário).
    admin_hash = _resolve_admin_hash()
    if admin_hash is None:
        return

    bind = op.get_bind()
    bind.execute(
        sa.text(
            "INSERT INTO users (id, username, password, email, full_name, active) VALUES "
            "(:id, 'admin', :pwd, 'admin@energyhub.local', 'Administrador', true) "
            "ON CONFLICT DO NOTHING"
        ),
        {"id": ADMIN_USER, "pwd": admin_hash},
    )

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
