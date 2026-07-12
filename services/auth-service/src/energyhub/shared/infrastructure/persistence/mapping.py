"""Mapeamento imperativo do **auth-service** (Fase 15).

Este serviço é dono **apenas** das tabelas de identidade/RBAC — `users`, `roles`, `permissions` e as
tabelas de junção. Ao contrário do monólito, NÃO mapeia entidades de outros contextos (o serviço
possui seu próprio banco e nunca lê as tabelas de outro serviço).
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import configure_mappers, relationship

from energyhub.auth.domain.entity.permission import Permission
from energyhub.auth.domain.entity.role import Role
from energyhub.auth.domain.entity.user import User
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


_configured = False


def configure_mappings() -> None:
    """Registra os mappers imperativos de identidade/RBAC (idempotente)."""
    global _configured
    if _configured:
        return

    registry.map_imperatively(Permission, permissions_table)
    registry.map_imperatively(
        Role,
        roles_table,
        properties={
            "permissions": relationship(
                Permission, secondary=role_permissions_table, lazy="selectin"
            ),
            "users": relationship(User, secondary=user_roles_table, back_populates="roles"),
        },
    )
    registry.map_imperatively(
        User,
        users_table,
        properties={
            "roles": relationship(
                Role, secondary=user_roles_table, back_populates="users", lazy="selectin"
            ),
        },
    )

    configure_mappers()
    _configured = True
