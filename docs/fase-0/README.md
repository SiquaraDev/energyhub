# 🧱 Fase 0 — Planejamento e Design do Sistema

Artefatos de **planejamento** do EnergyHub, produzidos **antes** de qualquer implementação.
Esta fase estabelece o escopo, os requisitos, o modelo de domínio e a arquitetura que guiam
todas as fases seguintes (ver [ROADMAP](../ROADMAP.md)).

> Todos os documentos são **spec-driven** e derivam da _change_
> [`openspec/changes/archive/2026-07-11-implement-fase-0`](../../openspec/changes/archive/2026-07-11-implement-fase-0/).
> Os diagramas usam **Mermaid** (versionável junto ao Markdown) e foram validados no _parser_ Mermaid v11.

---

## 📑 Documentos

| # | Documento | Conteúdo |
| :-: | :-------- | :------- |
| 01 | **[Escopo do Sistema](./01-escopo-do-sistema.md)** | Funcionalidades, tipos de usuário, 9 módulos, regras de negócio e fronteiras (In/Out of Scope) |
| 02 | **[Requisitos](./02-requisitos.md)** | 40 requisitos funcionais (RF) + 15 não-funcionais (RNF) com metas e critérios de aceitação |
| 03 | **[Casos de Uso](./03-casos-de-uso.md)** | 11 casos de uso (UC-01…UC-11) completos + diagrama de casos de uso |
| 04 | **[Modelo de Dados (DER)](./04-modelo-de-dados.md)** | 11 entidades de núcleo + apoio, relacionamentos e diagrama ER (PostgreSQL, 3FN) |
| 05 | **[Diagramas UML](./05-diagramas-uml.md)** | Diagramas de classes, sequência e componentes (DDD) |
| 06 | **[Eventos de Negócio](./06-eventos-de-negocio.md)** | 18 eventos com envelope, triggers, produtores, consumidores e payloads |
| 07 | **[Arquitetura](./07-arquitetura.md)** | Clean Architecture, módulos, camadas, regras de dependência e estrutura de diretórios |

---

## 🧭 Como ler

1. Comece pelo **[Escopo](./01-escopo-do-sistema.md)** para o panorama geral.
2. Aprofunde nos **[Requisitos](./02-requisitos.md)** e **[Casos de Uso](./03-casos-de-uso.md)** para o comportamento esperado.
3. Consulte **[Modelo de Dados](./04-modelo-de-dados.md)**, **[UML](./05-diagramas-uml.md)** e **[Eventos](./06-eventos-de-negocio.md)** para a estrutura e a dinâmica.
4. Finalize na **[Arquitetura](./07-arquitetura.md)**, que amarra tudo na organização de código da Fase 2 em diante.

---

## ✅ Cobertura (matriz de artefatos)

| Capacidade (OpenSpec) | Documento |
| :-------------------- | :-------- |
| `system-scope` | 01 |
| `requirements-specification` | 02 |
| `use-case-modeling` | 03 |
| `database-design` | 04 |
| `uml-modeling` | 05 |
| `business-events` | 06 |
| `architecture-planning` | 07 |

---

<sub>Voltar ao <a href="../README.md">índice da documentação</a> · <a href="../../README.md">README principal</a>.</sub>
