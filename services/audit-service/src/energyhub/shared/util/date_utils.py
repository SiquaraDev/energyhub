"""Utilitários de data/hora (sempre em UTC timezone-aware)."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Instante atual em UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


def to_iso(value: datetime) -> str:
    """Serializa um datetime no formato ISO-8601."""
    return value.isoformat()


def is_past(value: datetime) -> bool:
    """Indica se o instante informado já passou (em relação a agora, UTC)."""
    return value < utcnow()
