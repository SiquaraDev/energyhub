from __future__ import annotations

from energyhub.contracts.domain.entity.contract import Contract


class ContractAggregate:
    """Agregado de Contrato — raiz Contract, encapsula as transições de estado."""

    def __init__(self, contract: Contract) -> None:
        self._contract = contract

    def approve(self) -> None:
        """Aprova o contrato delegando à raiz do agregado."""
        self._contract.approve()

    def activate(self) -> None:
        """Ativa o contrato delegando à raiz do agregado."""
        self._contract.activate()

    def get_contract(self) -> Contract:
        """Retorna a raiz do agregado."""
        return self._contract
