"""Registro no Consul (service discovery) — helper reutilizável por todos os serviços (Fase 15).

Registra o serviço no agente Consul com **nome lógico**, **service id único por instância**
(`{name}-{instance_id}`, onde o discriminador é o `HOSTNAME` do pod ou um uuid4 por processo),
**endereço/porta** e um **health check HTTP** contra `/health` num intervalo definido — de modo que o
Consul reflita a saúde de cada instância e os chamadores (e o Traefik) a resolvam por nome.

O `Name` continua sendo o **nome lógico** do serviço: a descoberta por nome e o roteamento do Traefik
(provider Consul-catalog) não mudam. O que muda é que **cada réplica passa a ter uma entrada própria
no catálogo**, em vez de sobrescreverem umas às outras sob um id compartilhado.

Implementado via **HTTP API do Consul** (`httpx`, já dependência do serviço), em vez do
`python-consul` — funcionalmente idêntico, assíncrono-friendly e com uma dependência a menos.
"""

from __future__ import annotations

import logging
import os
import uuid

import httpx

logger = logging.getLogger(__name__)

# Discriminador estavel por PROCESSO: em k8s o HOSTNAME e o nome do pod (unico, legivel e ja
# injetado); fora do k8s (Compose/local) um uuid4 por processo evita colisao entre instancias.
# E o que torna o service_id unico por replica (antes era name-porta, igual em todas).
_INSTANCE_ID = os.environ.get("HOSTNAME", "").strip() or uuid.uuid4().hex[:12]


def _consul_base_url(consul_host: str, consul_port: int) -> str:
    return f"http://{consul_host}:{consul_port}"


def register_with_consul(
    *,
    name: str,
    port: int,
    address: str,
    consul_host: str,
    consul_port: int,
    health_path: str = "/health",
    interval: str = "10s",
    tags: list[str] | None = None,
) -> str:
    """Registra o serviço no Consul e devolve o `service_id` — `{name}-{instance_id}`, único por
    instância (o `instance_id` é o `HOSTNAME` do pod, ou um uuid4 por processo fora do k8s).

    O `Name` registrado continua sendo o **nome lógico** do serviço — a descoberta por nome e o
    roteamento Consul-catalog do Traefik não mudam; apenas cada réplica passa a ter uma entrada
    própria no catálogo, em vez de compartilhar (e sobrescrever) uma única.

    O health check aponta para `http://{address}:{port}{health_path}`; se a instância ficar crítica
    por mais de `1m`, o Consul a remove automaticamente do catálogo. `tags` alimenta o roteamento do
    Traefik (provider Consul-catalog): ex.: `traefik.http.routers.<r>.rule=PathPrefix(...)`.
    """
    service_id = f"{name}-{_INSTANCE_ID}"
    payload = {
        "Name": name,
        "ID": service_id,
        "Address": address,
        "Port": port,
        "Tags": tags or [],
        "Check": {
            "HTTP": f"http://{address}:{port}{health_path}",
            "Interval": interval,
            "Timeout": "5s",
            "DeregisterCriticalServiceAfter": "1m",
        },
    }
    try:
        with httpx.Client(base_url=_consul_base_url(consul_host, consul_port), timeout=10) as client:
            response = client.put("/v1/agent/service/register", json=payload)
            response.raise_for_status()
        logger.info("Registrado no Consul: %s (%s:%s)", service_id, address, port)
    except Exception:  # noqa: BLE001 — falha de registro não deve derrubar o serviço
        logger.warning("Falha ao registrar %s no Consul", service_id, exc_info=True)
    return service_id


def deregister_from_consul(*, service_id: str, consul_host: str, consul_port: int) -> None:
    """Remove o serviço do catálogo do Consul (chamar no shutdown)."""
    try:
        with httpx.Client(base_url=_consul_base_url(consul_host, consul_port), timeout=10) as client:
            client.put(f"/v1/agent/service/deregister/{service_id}")
        logger.info("Desregistrado do Consul: %s", service_id)
    except Exception:  # noqa: BLE001
        logger.warning("Falha ao desregistrar %s do Consul", service_id, exc_info=True)
