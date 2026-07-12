"""Hashing de senha com bcrypt.

Usa a lib `bcrypt` **diretamente**: o `passlib` 1.7.4 (declarado no projeto) é incompatível com
`bcrypt >= 4.1` (quebra ao ler `bcrypt.__about__`). O módulo compartilhado de segurança da Fase 7
poderá construir sobre estas funções.
"""

from __future__ import annotations

import bcrypt

# bcrypt trunca senhas com mais de 72 bytes; limitamos explicitamente para evitar erro.
_MAX_BCRYPT_BYTES = 72


def hash_password(plain: str) -> str:
    """Gera o hash bcrypt (custo 12) de uma senha em texto puro."""
    payload = plain.encode("utf-8")[:_MAX_BCRYPT_BYTES]
    return bcrypt.hashpw(payload, bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Confere uma senha em texto puro contra um hash bcrypt."""
    payload = plain.encode("utf-8")[:_MAX_BCRYPT_BYTES]
    return bcrypt.checkpw(payload, hashed.encode("utf-8"))
