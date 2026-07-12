from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from energyhub.negotiations.domain.entity.negotiation_status import NegotiationStatus
from energyhub.shared.domain.entity.base_entity import BaseEntity

if TYPE_CHECKING:
    from energyhub.contracts.domain.entity.contract import Contract


@dataclass(kw_only=True, eq=False)
class Negotiation(BaseEntity):
    """Negociação vinculada a um contrato (raiz do NegotiationAggregate)."""

    contract_id: UUID
    status: NegotiationStatus = NegotiationStatus.DRAFT
    contract: Contract | None = field(default=None, compare=False, repr=False)
