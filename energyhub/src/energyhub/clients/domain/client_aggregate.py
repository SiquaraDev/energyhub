from __future__ import annotations

from energyhub.clients.domain.entity.client import Client
from energyhub.clients.domain.entity.contact import Contact


class ClientAggregate:
    """Agregado de Cliente — raiz Client, fronteira de consistência com Contact."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def add_contact(self, contact: Contact) -> None:
        """Adiciona um contato ao cliente, mantendo a referência bidirecional."""
        contact.client_id = self._client.id
        contact.client = self._client
        if contact not in self._client.contacts:
            self._client.contacts.append(contact)
            self._client.update_timestamp()

    def remove_contact(self, contact: Contact) -> None:
        """Remove um contato do cliente."""
        if contact in self._client.contacts:
            self._client.contacts.remove(contact)
            self._client.update_timestamp()

    def activate(self) -> None:
        """Ativa o cliente e atualiza o timestamp."""
        self._client.active = True
        self._client.update_timestamp()

    def deactivate(self) -> None:
        """Desativa o cliente e atualiza o timestamp."""
        self._client.active = False
        self._client.update_timestamp()

    def get_client(self) -> Client:
        """Retorna a raiz do agregado."""
        return self._client
