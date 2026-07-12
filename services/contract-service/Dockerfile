# contract-service — imagem multi-stage (Fase 15). Contexto de build = este diretório.
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install .

FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv

RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8003
CMD ["uvicorn", "energyhub.main:app", "--host", "0.0.0.0", "--port", "8003"]
