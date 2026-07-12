"""Métricas de negócio (Fase 12).

`BusinessMetrics` obtém os coletores do `MetricsConfig` e registra eventos de negócio (clientes
criados, contratos por status, faturas pagas, clientes ativos) + a duração das operações. As séries
rotuladas são **inicializadas em zero** no startup (dashboards renderizam antes do 1º evento).

O registro de métricas é um **efeito colateral livre de falhas**: use `record_safely` para que um
erro de métrica nunca quebre a operação de negócio subjacente.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable

from energyhub.shared.infrastructure.metrics.metrics_config import MetricsConfig

logger = logging.getLogger(__name__)


class BusinessMetrics:
    """Fachada de registro dos eventos de negócio (obtém os coletores do `MetricsConfig`)."""

    def __init__(self) -> None:
        self._client_created = MetricsConfig.client_created_counter()
        self._contract_created = MetricsConfig.contract_created_counter()
        self._invoice_paid = MetricsConfig.invoice_paid_counter()
        self._active_clients = MetricsConfig.active_clients_gauge()
        self._duration = MetricsConfig.request_duration_histogram()

    def initialize(self, contract_statuses: Iterable[str]) -> None:
        """Inicializa as séries rotuladas em zero (recebe os status do chamador — sem dependência
        de `shared` para os módulos de negócio)."""
        self._client_created.inc(0)
        self._invoice_paid.inc(0)
        self._active_clients.set(0)
        for status in contract_statuses:
            self._contract_created.labels(status=status)

    def increment_client_created(self) -> None:
        self._client_created.inc()

    def increment_contract_created(self, status: str) -> None:
        self._contract_created.labels(status=status).inc()

    def increment_invoice_paid(self) -> None:
        self._invoice_paid.inc()

    def set_active_clients(self, count: int) -> None:
        self._active_clients.set(count)

    def observe_operation(self, endpoint: str, method: str, seconds: float) -> None:
        self._duration.labels(endpoint=endpoint, method=method).observe(seconds)


#: Instância compartilhada (coletores registrados uma vez; inicializada no lifespan).
business_metrics = BusinessMetrics()


def record_safely(action: Callable[[], None]) -> None:
    """Executa o registro de métrica engolindo qualquer erro (nunca quebra a operação)."""
    try:
        action()
    except Exception as error:  # noqa: BLE001 (métrica não é crítica)
        logger.warning("Falha ao registrar métrica (ignorada): %s", error)
