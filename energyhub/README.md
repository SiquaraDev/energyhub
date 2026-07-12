# ⚡ EnergyHub — Backend

_Backend_ da plataforma de negociação de energia **EnergyHub**, construído com **FastAPI**,
**Clean Architecture** e **Domain-Driven Design (DDD)**, usando **layout `src`** e **Poetry**.

> Este é o README do pacote Python (subpasta `energyhub/`). Para a visão geral do projeto,
> veja o [README principal](../README.md).

---

## 📂 Estrutura

```
src/energyhub/
├── main.py                 # app FastAPI (endpoints / e /health, CORS)
├── config/                 # pacote: settings.py + reexport + dependencies/ (DI)
├── shared/                 # classes-base + utilitários compartilhados
│   ├── domain/             #   BaseEntity, Repository, DomainException (+3)
│   ├── application/        #   BaseDTO, UseCase, ApplicationException
│   ├── infrastructure/     #   SQLAlchemyRepository
│   ├── presentation/       #   BaseRouter, ErrorResponse, global_exception_handler
│   └── util/ constant/ enums/
├── auth/ clients/ contracts/ negotiations/    # 8 módulos de negócio,
└── financial/ audit/ notifications/ reports/  # cada um com as 4 camadas
```

Cada módulo de negócio segue as **4 camadas** da Clean Architecture — `domain/`,
`application/`, `infrastructure/` e `presentation/` — com a regra de dependência estrita
(o domínio não depende de nada; a aplicação depende do domínio; a infraestrutura implementa
as interfaces do domínio). Os testes ficam em `tests/`.

---

## 🚀 Como rodar

```bash
cd energyhub
poetry install
poetry run uvicorn energyhub.main:app --reload
```

A API sobe em **http://localhost:8000**:

```bash
curl http://localhost:8000/           # {"message": "EnergyHub API"}
curl http://localhost:8000/health     # {"status": "healthy"}
```

Documentação interativa (Swagger UI) em **http://localhost:8000/docs**.

---

## 🧪 Testes

```bash
poetry run pytest
```

---

## 🧰 Qualidade de código

```bash
poetry run black .        # formatação
poetry run ruff check .   # lint
poetry run mypy .         # checagem de tipos
```

---

## 📚 Links

- [README principal](../README.md) — visão geral, arquitetura e roadmap
- [Documentação](../docs/) — índice, ROADMAP e CHANGELOG
