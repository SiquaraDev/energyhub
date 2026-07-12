# EnergyHub — imagem da aplicação (Fase 14).
#
# Build multi-stage: o estágio `builder` resolve APENAS as dependências de produção com o Poetry
# num virtualenv (`/build/.venv`); o estágio `runtime` copia só esse venv + o código da aplicação,
# roda como usuário não-root (`appuser`) e sobe a API com uvicorn. Contexto de build = raiz do repo
# (o projeto Python vive em `energyhub/`); ver `.dockerignore`.
#
# Build:  docker build -t energyhub:latest .
# Run:    docker run -p 8000:8000 --env-file .env energyhub:latest

# ---------- Estágio de build: dependências de produção ----------
FROM python:3.12-slim AS builder

ENV POETRY_VERSION=2.4.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# WORKDIR = /app (mesmo caminho do runtime) para que o venv seja criado em `/app/.venv`: assim os
# shebangs dos console scripts (uvicorn/alembic) apontam para `/app/.venv/bin/python`, que existe
# no estágio de runtime (senão o exec falha com "no such file or directory").
WORKDIR /app
# Só os manifestos primeiro: aproveita o cache de camadas do Docker (deps não reinstalam quando
# apenas o código-fonte muda). `--only main` exclui o grupo `dev` (pytest, ruff, mypy...);
# `--no-root` não instala o pacote do projeto (o código é copiado e servido via PYTHONPATH).
COPY energyhub/pyproject.toml energyhub/poetry.lock energyhub/README.md ./
RUN poetry install --only main --no-root

# ---------- Estágio de runtime: slim, não-root, sem toolchain de build ----------
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/src

WORKDIR /app

# Só o venv resolvido (deps + console scripts uvicorn/alembic) — sem Poetry nem compiladores.
COPY --from=builder /app/.venv /app/.venv
# Código da aplicação + migrações (o pacote é importado via PYTHONPATH=/app/src).
COPY energyhub/src ./src
COPY energyhub/alembic ./alembic
COPY energyhub/alembic.ini ./alembic.ini

# Usuário não-root; a aplicação não escreve nos volumes de dados (pertencem às imagens oficiais).
RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "energyhub.main:app", "--host", "0.0.0.0", "--port", "8000"]
