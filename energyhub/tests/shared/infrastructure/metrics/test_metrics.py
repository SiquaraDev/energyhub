"""Testes unitários das métricas de negócio/sistema (registro livre de falhas)."""

from __future__ import annotations

from energyhub.shared.infrastructure.metrics.business_metrics import (
    business_metrics,
    record_safely,
)
from energyhub.shared.infrastructure.metrics.metrics_config import (
    MetricsConfig,
    set_application_info,
)
from energyhub.shared.infrastructure.metrics.system_metrics import (
    register_system_metrics,
    update_system_metrics,
)


def test_business_metrics_operations_do_not_raise() -> None:
    business_metrics.initialize(["DRAFT", "ACTIVE"])
    business_metrics.increment_client_created()
    business_metrics.increment_contract_created("ACTIVE")
    business_metrics.increment_invoice_paid()
    business_metrics.set_active_clients(7)
    business_metrics.observe_operation("client_create", "POST", 0.01)


def test_record_safely_runs_action() -> None:
    calls: list[int] = []
    record_safely(lambda: calls.append(1))
    assert calls == [1]


def test_record_safely_swallows_exceptions() -> None:
    def boom() -> None:
        raise RuntimeError("métrica quebrou")

    # Não deve propagar: métrica nunca quebra a operação de negócio.
    record_safely(boom)


def test_metrics_config_exposes_collectors() -> None:
    assert MetricsConfig.client_created_counter() is not None
    assert MetricsConfig.contract_created_counter() is not None
    assert MetricsConfig.invoice_paid_counter() is not None
    assert MetricsConfig.active_clients_gauge() is not None
    assert MetricsConfig.request_duration_histogram() is not None


def test_set_application_info_does_not_raise() -> None:
    set_application_info("EnergyHub", "test", "0.13.0")


def test_system_metrics_register_and_update_are_idempotent() -> None:
    register_system_metrics()
    register_system_metrics()  # idempotente
    update_system_metrics()
