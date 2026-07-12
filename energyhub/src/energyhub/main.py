"""Ponto de entrada da aplicação FastAPI do EnergyHub."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EnergyHub",
    description="Energy Trading Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Endpoint raiz."""
    return {"message": "EnergyHub API"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check da aplicação."""
    return {"status": "healthy"}
