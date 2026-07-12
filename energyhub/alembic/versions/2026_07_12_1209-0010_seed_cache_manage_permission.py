"""seed CACHE_MANAGE permission and grant it to ADMIN (Fase 9)

Revision ID: 0010
Revises: 0009
Create Date: 2026-07-12 12:09:00.000000+00:00

Adiciona a permissão `CACHE_MANAGE` (usada para proteger os endpoints de administração do cache
`/api/v1/cache`) e a concede ao papel ADMIN. O nome espelha
`energyhub.shared.constant.permissions.CACHE_MANAGE`.
"""

from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ROLE_ADMIN = "11111111-1111-1111-1111-111111111111"
CACHE_MANAGE_ID = "00000000-0000-0000-0000-000000000b01"


def upgrade() -> None:
    op.execute(f"""
        INSERT INTO permissions (id, name, description) VALUES
            ('{CACHE_MANAGE_ID}', 'CACHE_MANAGE', 'Gerenciar o cache (estatísticas e limpeza)')
        ON CONFLICT DO NOTHING;
        """)
    op.execute(f"""
        INSERT INTO role_permissions (role_id, permission_id) VALUES
            ('{ROLE_ADMIN}', '{CACHE_MANAGE_ID}')
        ON CONFLICT DO NOTHING;
        """)


def downgrade() -> None:
    op.execute(
        f"DELETE FROM role_permissions WHERE role_id = '{ROLE_ADMIN}' "
        f"AND permission_id = '{CACHE_MANAGE_ID}'"
    )
    op.execute(f"DELETE FROM permissions WHERE id = '{CACHE_MANAGE_ID}'")
