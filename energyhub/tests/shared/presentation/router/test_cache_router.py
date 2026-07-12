"""Testes de componente do `CacheRouter` (`/api/v1/cache`; sem Redis)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest


def test_cache_stats_returns_backend_and_prefix(router_client: Any) -> None:
    # A fixture autouse `_cache_backend` já inicializa um InMemoryBackend.
    from energyhub.shared.presentation.router.cache_router import CacheRouter

    api = router_client(CacheRouter().get_router())

    response = api.get("/api/v1/cache/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["backend"] == "InMemoryBackend"
    assert body["prefix"] == "energyhub"


def test_cache_clear_returns_message(router_client: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    # `invalidate_all_cache` fala com Redis; substituído por um double no namespace do router.
    from energyhub.shared.presentation.router import cache_router

    monkeypatch.setattr(cache_router, "invalidate_all_cache", AsyncMock())
    api = router_client(cache_router.CacheRouter().get_router())

    response = api.post("/api/v1/cache/clear")

    assert response.status_code == 200
    assert "message" in response.json()
