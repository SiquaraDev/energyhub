"""Métricas de recursos do host (psutil · Fase 12).

`SystemMetricsCollector` é um _collector_ Prometheus que **atualiza os gauges no momento do scrape**
(`collect()` chama `update_system_metrics()` antes de emitir os samples), então os valores refletem
o estado atual do host — não um snapshot do startup. Expõe `memory_usage_bytes`, `cpu_usage_percent`
e `disk_usage_percent`.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import psutil
from prometheus_client import REGISTRY, Gauge
from prometheus_client.core import Metric

# Raiz do disco a medir (cross-platform: "C:\\" no Windows, "/" no Linux).
_DISK_ROOT = Path.cwd().anchor or "/"


class SystemMetricsCollector:
    """Coletor que refresca os gauges de recurso do host via psutil a cada scrape."""

    def __init__(self) -> None:
        # `registry=None`: os gauges não se auto-registram; este coletor os expõe em `collect()`.
        self._memory = Gauge("memory_usage_bytes", "Uso de memória do host em bytes", registry=None)
        self._memory_available = Gauge(
            "memory_available_bytes", "Memória disponível do host em bytes", registry=None
        )
        self._cpu = Gauge("cpu_usage_percent", "Uso de CPU do host em %", registry=None)
        self._disk = Gauge("disk_usage_percent", "Uso de disco do host em %", registry=None)

    def update_system_metrics(self) -> None:
        """Atualiza os gauges a partir do psutil (memória usada/disponível, CPU %, disco %)."""
        memory = psutil.virtual_memory()
        self._memory.set(memory.used)
        self._memory_available.set(memory.available)
        self._cpu.set(psutil.cpu_percent(interval=None))
        self._disk.set(psutil.disk_usage(_DISK_ROOT).percent)

    def collect(self) -> Iterator[Metric]:
        """Refresca e emite os samples (chamado pelo registry a cada scrape)."""
        self.update_system_metrics()
        yield from self._memory.collect()
        yield from self._memory_available.collect()
        yield from self._cpu.collect()
        yield from self._disk.collect()


_collector = SystemMetricsCollector()


def register_system_metrics() -> None:
    """Registra o coletor de recursos no registry default (idempotente) e prima o CPU%."""
    try:
        REGISTRY.register(_collector)
    except ValueError:
        pass  # já registrado (ex.: reload)
    psutil.cpu_percent(interval=None)  # prima o delta de CPU (1ª leitura seria 0)


def update_system_metrics() -> None:
    """Atualiza os gauges de recurso do host (delegado ao coletor)."""
    _collector.update_system_metrics()
