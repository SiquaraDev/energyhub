"""Predicados componíveis de consulta para `Client` (construtores de condição SQLAlchemy)."""

from __future__ import annotations

from sqlalchemy.sql.elements import ColumnElement

from energyhub.clients.domain.entity.client import Client
from energyhub.clients.domain.entity.contact import Contact
from energyhub.clients.domain.entity.contact_type import ContactType


class ClientFilter:
    """Cada método retorna uma condição SQLAlchemy; combine-as via `and_`/`or_` no repositório."""

    @staticmethod
    def has_cnpj(cnpj: str) -> ColumnElement[bool]:
        return Client.cnpj == cnpj

    @staticmethod
    def has_corporate_name(name: str) -> ColumnElement[bool]:
        return Client.corporate_name.ilike(f"%{name}%")

    @staticmethod
    def is_active(active: bool = True) -> ColumnElement[bool]:
        return Client.active.is_(active)

    @staticmethod
    def has_city(city: str) -> ColumnElement[bool]:
        return Client.city == city

    @staticmethod
    def has_state(state: str) -> ColumnElement[bool]:
        return Client.state == state

    @staticmethod
    def with_contact_type(contact_type: ContactType) -> ColumnElement[bool]:
        return Client.contacts.any(Contact.type == contact_type)
