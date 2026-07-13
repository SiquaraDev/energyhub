"""flag admin bootstrap credential for rotation on first use

Revision ID: 0011
Revises: 0010
Create Date: 2026-07-13 10:00:00.000000+00:00

Parte da change `harden-security-credentials`: adiciona a coluna `require_password_rotation` à
tabela `users` e, fora do perfil `development`, marca o admin de bootstrap para trocar a senha no
primeiro uso — de modo que a credencial de bootstrap não persista. Coluna não-mapeada pelo ORM
(o mapeamento imperativo lista colunas explicitamente), logo não afeta entidades/repositórios.
"""

import os
from collections.abc import Sequence
from typing import Union

from alembic import op

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Coluna de flag (idempotente); default false para os usuários existentes.
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
        "require_password_rotation BOOLEAN NOT NULL DEFAULT false"
    )

    # Fora de dev, o admin de bootstrap deve rotacionar a senha no primeiro uso.
    if os.environ.get("ENVIRONMENT", "development").strip().lower() != "development":
        op.execute("UPDATE users SET require_password_rotation = true WHERE username = 'admin'")


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS require_password_rotation")
