"""Base para clientes HTTP entre serviços (Fase 15).

Reúne descoberta por Consul (resolução por **nome lógico**, com fallback DNS) e a política de
resiliência exigida em toda chamada de rede: **timeout** explícito, **retry** com _backoff_
exponencial (`tenacity`, tentativas limitadas) para falhas transientes, `raise_for_status` para
surfaçar erros de upstream, e um **fallback** (`None`) quando as tentativas se esgotam — de modo que a
falha de uma dependência não cascateie pela cadeia da requisição.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from energyhub.config import settings

logger = logging.getLogger(__name__)

# Falhas transientes que justificam retry (rede/timeout). Erros HTTP 4xx/5xx propagam → fallback.
_TRANSIENT = (httpx.TransportError, httpx.TimeoutException)


class ServiceClient:
    """Cliente HTTP resiliente para um serviço upstream, resolvido por nome via Consul."""

    def __init__(self, service_name: str, default_port: int, *, timeout: float = 5.0) -> None:
        self._service_name = service_name
        self._default_port = default_port
        # Timeout explícito (§8.1): uma dependência lenta/travada não bloqueia o chamador sem limite.
        # Credencial inter-servico (harden-security-credentials): toda chamada carrega o header
        # X-Internal-Api-Key exigido pelas rotas /internal/* do auth-service.
        _headers = (
            {"X-Internal-Api-Key": settings.internal_api_key} if settings.internal_api_key else {}
        )
        self._client = httpx.AsyncClient(timeout=timeout, headers=_headers)

    async def _resolve_base_url(self) -> str:
        """Resolve uma instância saudável via catálogo do Consul; fallback = nome lógico (DNS)."""
        try:
            response = await self._client.get(
                f"http://{settings.consul_host}:{settings.consul_port}"
                f"/v1/health/service/{self._service_name}?passing",
                timeout=3.0,
            )
            response.raise_for_status()
            instances = response.json()
            if instances:
                service = instances[0]["Service"]
                return f"http://{service['Address']}:{service['Port']}"
        except Exception:  # noqa: BLE001 — indisponibilidade do Consul cai no fallback por nome
            logger.debug("Lookup no Consul falhou para %s; usando DNS", self._service_name)
        return f"http://{self._service_name}:{self._default_port}"

    async def _get(self, path: str) -> Any | None:
        """GET resiliente: timeout + retry com backoff; fallback `None` ao esgotar (§8.3)."""
        try:
            return await self._get_with_retry(path)
        except Exception:  # noqa: BLE001 — retries esgotados/erro → falha contida
            logger.warning("Chamada a %s%s falhou; fallback=None", self._service_name, path)
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.2, max=2.0),
        retry=retry_if_exception_type(_TRANSIENT),
        reraise=True,
    )
    async def _get_with_retry(self, path: str) -> Any:
        base_url = await self._resolve_base_url()
        response = await self._client.get(f"{base_url}{path}")
        response.raise_for_status()  # erros de upstream surgem explicitamente
        return response.json()

    async def close(self) -> None:
        """Libera o pool de conexões `httpx` (chamar no shutdown do serviço)."""
        await self._client.aclose()
