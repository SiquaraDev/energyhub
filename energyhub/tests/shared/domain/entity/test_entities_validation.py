"""Testes de validação (`__post_init__`) das entidades de domínio dos demais módulos."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from energyhub.audit.domain.entity.audit_action import AuditAction
from energyhub.audit.domain.entity.audit_log import AuditLog
from energyhub.clients.domain.entity.client import Client
from energyhub.clients.domain.entity.contact import Contact
from energyhub.clients.domain.entity.contact_type import ContactType
from energyhub.financial.domain.entity.invoice import Invoice
from energyhub.financial.domain.entity.invoice_status import InvoiceStatus
from energyhub.financial.domain.entity.payment import Payment
from energyhub.notifications.domain.entity.notification import Notification
from energyhub.reports.domain.entity.report import Report
from energyhub.shared.domain.exception.validation_exception import ValidationException


def test_client_requires_cnpj_and_corporate_name() -> None:
    with pytest.raises(ValidationException):
        Client(cnpj="", corporate_name="Alpha")
    with pytest.raises(ValidationException):
        Client(cnpj="11222333000181", corporate_name="  ")


def test_contact_requires_name() -> None:
    with pytest.raises(ValidationException):
        Contact(client_id=uuid4(), name="  ", type=ContactType.PRIMARY)


def test_invoice_rejects_negative_amount_but_allows_zero() -> None:
    with pytest.raises(ValidationException):
        Invoice(
            invoice_number="INV-1",
            client_id=uuid4(),
            amount=Decimal("-1"),
            due_date=datetime.now(timezone.utc).date(),
            status=InvoiceStatus.DRAFT,
        )
    zero = Invoice(
        invoice_number="INV-2",
        client_id=uuid4(),
        amount=Decimal("0"),
        due_date=datetime.now(timezone.utc).date(),
        status=InvoiceStatus.DRAFT,
    )
    assert zero.amount == Decimal("0")


def test_payment_rejects_non_positive_amount() -> None:
    with pytest.raises(ValidationException):
        Payment(
            invoice_id=uuid4(),
            amount=Decimal("0"),
            payment_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )


def test_notification_requires_title_and_message() -> None:
    with pytest.raises(ValidationException):
        Notification(user_id=uuid4(), title="  ", message="corpo")
    with pytest.raises(ValidationException):
        Notification(user_id=uuid4(), title="Oi", message="   ")


def test_report_requires_report_type() -> None:
    with pytest.raises(ValidationException):
        Report(report_type="  ", generated_by=uuid4())


def test_audit_log_requires_entity_type() -> None:
    with pytest.raises(ValidationException):
        AuditLog(
            user_id=uuid4(),
            action=AuditAction.CREATE,
            entity_type="  ",
            entity_id=uuid4(),
        )
