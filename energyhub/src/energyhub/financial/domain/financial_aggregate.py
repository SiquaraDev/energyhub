from __future__ import annotations

from energyhub.financial.domain.entity.invoice import Invoice
from energyhub.financial.domain.entity.payment import Payment


class FinancialAggregate:
    """Agregado Financeiro — raiz Invoice, fronteira de consistência com Payment."""

    def __init__(self, invoice: Invoice) -> None:
        self._invoice = invoice
        self._payments: list[Payment] = []

    def add_payment(self, payment: Payment) -> None:
        """Vincula um pagamento à fatura (bidirecional) e o adiciona ao agregado."""
        payment.invoice_id = self._invoice.id
        payment.invoice = self._invoice
        if payment not in self._payments:
            self._payments.append(payment)

    def remove_payment(self, payment: Payment) -> None:
        """Remove um pagamento do agregado."""
        if payment in self._payments:
            self._payments.remove(payment)

    def get_payments(self) -> list[Payment]:
        """Retorna os pagamentos vinculados à fatura."""
        return self._payments

    def get_invoice(self) -> Invoice:
        """Retorna a fatura raiz do agregado."""
        return self._invoice
