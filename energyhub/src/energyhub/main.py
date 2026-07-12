"""Ponto de entrada da aplicação FastAPI do EnergyHub."""

from fastapi import FastAPI

app = FastAPI(
    title="EnergyHub",
    description="Energy Trading Platform",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Endpoint raiz."""
    return {"message": "EnergyHub API"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check da aplicação."""
    return {"status": "healthy"}
