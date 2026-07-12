from __future__ import annotations

from enum import Enum


class TransactionType(str, Enum):
    """Tipo de transação de energia (compra ou venda)."""

    BUY = "BUY"
    SELL = "SELL"
