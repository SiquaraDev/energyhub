"""Fixtures compartilhadas dos testes do EnergyHub."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from energyhub.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Cliente de teste da aplicação FastAPI."""
    with TestClient(app) as test_client:
        yield test_client
