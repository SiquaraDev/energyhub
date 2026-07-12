from __future__ import annotations

from energyhub.negotiations.domain.entity.energy_transaction import EnergyTransaction
from energyhub.negotiations.domain.entity.negotiation import Negotiation


class NegotiationAggregate:
    """Agregado de Negociação — raiz Negotiation, fronteira com EnergyTransaction."""

    def __init__(self, negotiation: Negotiation) -> None:
        self._negotiation = negotiation
        self._transactions: list[EnergyTransaction] = []

    def add_transaction(self, transaction: EnergyTransaction) -> None:
        """Adiciona uma transação à negociação, vinculando referência e id."""
        transaction.negotiation_id = self._negotiation.id
        transaction.negotiation = self._negotiation
        if transaction not in self._transactions:
            self._transactions.append(transaction)

    def remove_transaction(self, transaction: EnergyTransaction) -> None:
        """Remove uma transação da negociação."""
        if transaction in self._transactions:
            self._transactions.remove(transaction)

    def get_transactions(self) -> list[EnergyTransaction]:
        """Retorna as transações da negociação."""
        return self._transactions

    def get_negotiation(self) -> Negotiation:
        """Retorna a negociação (raiz do agregado)."""
        return self._negotiation
