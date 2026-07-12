# 📚 Documentação — EnergyHub

Índice da documentação da plataforma **EnergyHub** (negociação de energia · FastAPI · Clean Architecture · DDD).

> Para a **visão geral completa** do projeto (funcionalidades, arquitetura, stack, como executar),
> veja o **[README principal](../README.md)** na raiz do repositório.

> 📌 **Estado:** Fases 0–15 implementadas (versão `0.15.0`); a próxima é a **Fase 16**.

---

## 🧭 Documentos

| Documento | O que você encontra |
| :-------- | :------------------ |
| 📄 **[README principal](../README.md)** | Visão geral, arquitetura, modelo de domínio, stack e guia de _getting started_ |
| 🧱 **[fase-0/](./fase-0/README.md)** | Artefatos de **planejamento e design** (Fase 0): escopo, requisitos, casos de uso, DER, UML, eventos de negócio e arquitetura |
| 🏗️ **[ARCHITECTURE.md](./ARCHITECTURE.md)** | Guia da arquitetura como-construída (Clean Architecture, classes-base, domínio, schema do banco, persistência, API REST, segurança JWT/RBAC, documentação/erros da API, cache Redis, mensageria RabbitMQ/Kafka, busca Elasticsearch, observabilidade Prometheus/Grafana, estratégia de testes e a containerização Docker/Compose — Fases 2–14) |
| 🧩 **[bounded-contexts.md](./bounded-contexts.md)** | Decomposição em microsserviços (Fase 15): inventário módulo→contexto→serviço, grafo de dependências (DAG), ordem de extração e regras (banco por serviço, HTTP + discovery + gateway) |
| 🚨 **[API_ERRORS.md](./API_ERRORS.md)** | Catálogo de erros da API: formatos `ErrorResponse`/`ValidationErrorResponse`, status HTTP e `error_code` por módulo |
| 🧪 **[API_EXAMPLES.md](./API_EXAMPLES.md)** | Exemplos `curl` dos fluxos principais (login → CRUD de clientes) com o cabeçalho `Authorization: Bearer` |
| 🗺️ **[ROADMAP.md](./ROADMAP.md)** | Plano de evolução detalhado das **18 fases**, agrupadas em 7 etapas, com objetivos, entregáveis, decisões-chave e mapa de dependências |
| 📜 **[CHANGELOG.md](./CHANGELOG.md)** | Histórico de versões planejadas (fase → versão, `0.1.0` → `1.0.0`) no formato [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) + [SemVer](https://semver.org/lang/pt-BR/) |
| 📋 **[openspec/changes/](../openspec/changes/)** | Especificações _spec-driven_ completas: `proposal.md`, `design.md`, `tasks.md` e _specs_ por capacidade |

---

## 🗂️ Documentos futuros

Estes artefatos serão adicionados nas fases indicadas:

| Documento | Fase | Conteúdo |
| :-------- | :--: | :------- |
| `docs/ci-cd.md` | 17 | Pipeline de CI/CD ponta-a-ponta (build → testes → publicação → deploy) |

---

## 🧩 Como este projeto é organizado

O EnergyHub é construído de forma **incremental e _spec-driven_**: cada fase é uma _change_ do
[OpenSpec](../openspec/) especificada **antes** da implementação. O fluxo, resumidamente:

```
Proposta (proposal.md) → Design (design.md) → Tarefas (tasks.md) → Specs (specs/) → Implementação
```

Consulte o [ROADMAP](./ROADMAP.md) para a sequência completa das 18 fases e o
[CHANGELOG](./CHANGELOG.md) para o mapeamento fase → versão.

---

<sub>Voltar ao <a href="../README.md">README principal</a>.</sub>
