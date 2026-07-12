"""Constantes de cache (Fase 9 — Redis).

`CacheConstants` centraliza os **namespaces por domínio** e os **TTLs** (tiers por volatilidade),
mantendo os decoradores `@cache` e as chamadas de invalidação em sincronia (namespace/TTL nunca
literais espalhados). O prefixo global das chaves é `CACHE_KEY_PREFIX`.
"""

# Prefixo global das chaves do cache (isola o keyspace do EnergyHub no Redis).
CACHE_KEY_PREFIX = "energyhub"

# Constantes de módulo pré-existentes (mantidas por compatibilidade).
DEFAULT_CACHE_TTL_SECONDS = 300
SHORT_CACHE_TTL_SECONDS = 60
LONG_CACHE_TTL_SECONDS = 3600


class CacheConstants:
    """Namespaces de domínio e TTLs reutilizáveis para o cache de leitura."""

    # --- Namespaces por domínio (usados no `@cache(namespace=...)` e na invalidação) ---
    ROLES = "roles"
    PERMISSIONS = "permissions"
    CLIENTS = "clients"
    CONTRACTS = "contracts"
    USERS = "users"

    # --- TTLs (segundos) — tiers distintos e crescentes por volatilidade dos dados ---
    SHORT_TTL = 300  # dados mais mutáveis (ex.: clientes)
    DEFAULT_TTL = 600  # padrão
    LONG_TTL = 3600  # dados de referência, raramente mudam (ex.: papéis/permissões)
