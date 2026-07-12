"""Fábrica central de coletores Prometheus (Fase 12).

`MetricsConfig` define os coletores customizados (counters/gauges/histogram) **uma única vez** — os
coletores Prometheus precisam ser registrados uma vez por nome, então concentrá-los aqui evita o
erro de registro duplicado e mantém nomes/labels consistentes. Também expõe o `application_info`.
"""

from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram, Info


class MetricsConfig:
    """Catálogo único dos coletores customizados da aplicação."""

    # --- Métricas de negócio ---
    CLIENT_CREATED = Counter("client_created_total", "Total de clientes criados")
    CONTRACT_CREATED = Counter(
        "contract_created_total", "Total de contratos criados, por status", ["status"]
    )
    INVOICE_PAID = Counter("invoice_paid_total", "Total de faturas pagas")
    ACTIVE_CLIENTS = Gauge("clients_active", "Número de clientes ativos")

    # --- Duração de operações de serviço (labels: endpoint, method) ---
    OPERATION_DURATION = Histogram(
        "operation_duration_seconds", "Duração de operações de serviço (s)", ["endpoint", "method"]
    )

    # --- Informações da aplicação (expõe `application_info{name,environment,version}`) ---
    APPLICATION_INFO = Info("application", "Informações da aplicação (nome, ambiente, versão)")

    @staticmethod
    def client_created_counter() -> Counter:
        return MetricsConfig.CLIENT_CREATED

    @staticmethod
    def contract_created_counter() -> Counter:
        return MetricsConfig.CONTRACT_CREATED

    @staticmethod
    def invoice_paid_counter() -> Counter:
        return MetricsConfig.INVOICE_PAID

    @staticmethod
    def active_clients_gauge() -> Gauge:
        return MetricsConfig.ACTIVE_CLIENTS

    @staticmethod
    def request_duration_histogram() -> Histogram:
        return MetricsConfig.OPERATION_DURATION

    @staticmethod
    def application_info() -> Info:
        return MetricsConfig.APPLICATION_INFO


def set_application_info(name: str, environment: str, version: str) -> None:
    """Popula o `application_info` a partir das settings (nome/ambiente/versão)."""
    MetricsConfig.APPLICATION_INFO.info(
        {"name": name, "environment": environment, "version": version}
    )
