"""DTO de resposta de contato."""

from __future__ import annotations

from uuid import UUID

from energyhub.clients.domain.entity.contact_type import ContactType
from energyhub.shared.application.dto.base_dto import BaseDTO


class ContactResponseDTO(BaseDTO):
    """Representação de saída de um contato (inclui id/timestamps do `BaseDTO`)."""

    client_id: UUID
    name: str
    type: ContactType
    email: str | None = None
    phone: str | None = None
    position: str | None = None
