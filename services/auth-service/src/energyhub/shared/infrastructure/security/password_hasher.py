"""Módulo compartilhado de hashing de senha (BCrypt).

O plano da Fase 7 previa um `passlib` `CryptContext`, mas o `passlib` 1.7.4 é **incompatível**
com o `bcrypt >= 4.1` instalado (quebra em runtime ao ler `bcrypt.__about__.__version__`, removido
no `bcrypt` 4.1+). Usamos, portanto, a lib `bcrypt` **diretamente** — a intenção da spec (hash
BCrypt com sal, verificação em tempo constante) é preservada, sem o import quebrado.

API pública (nomes exigidos pela spec da Fase 7):
- `get_password_hash(plain) -> str`  — gera o hash BCrypt (custo 12).
- `verify_password(plain, hashed) -> bool` — confere a senha contra o hash.
"""

from __future__ import annotations

import bcrypt

# bcrypt trunca senhas com mais de 72 bytes; limitamos explicitamente para evitar erro.
_MAX_BCRYPT_BYTES = 72
_BCRYPT_ROUNDS = 12


def get_password_hash(plain: str) -> str:
    """Gera o hash BCrypt (custo 12) de uma senha em texto puro."""
    payload = plain.encode("utf-8")[:_MAX_BCRYPT_BYTES]
    return bcrypt.hashpw(payload, bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Confere uma senha em texto puro contra um hash BCrypt."""
    payload = plain.encode("utf-8")[:_MAX_BCRYPT_BYTES]
    return bcrypt.checkpw(payload, hashed.encode("utf-8"))


# Alias retrocompatível: o `UserService` (Fase 6) importa `hash_password`.
hash_password = get_password_hash
