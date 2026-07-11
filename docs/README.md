# 📚 Documentação — EnergyHub

Índice da documentação da plataforma **EnergyHub** (negociação de energia · FastAPI · Clean Architecture · DDD).

> Para a **visão geral completa** do projeto (funcionalidades, arquitetura, stack, como executar),
> veja o **[README principal](../README.md)** na raiz do repositório.

---

## 🧭 Documentos

| Documento | O que você encontra |
| :-------- | :------------------ |
| 📄 **[README principal](../README.md)** | Visão geral, arquitetura, modelo de domínio, stack e guia de _getting started_ |
| 🗺️ **[ROADMAP.md](./ROADMAP.md)** | Plano de evolução detalhado das **18 fases**, agrupadas em 7 etapas, com objetivos, entregáveis, decisões-chave e mapa de dependências |
| 📜 **[CHANGELOG.md](./CHANGELOG.md)** | Histórico de versões planejadas (fase → versão, `0.1.0` → `1.0.0`) no formato [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) + [SemVer](https://semver.org/lang/pt-BR/) |
| 📋 **[openspec/changes/](../openspec/changes/)** | Especificações _spec-driven_ completas: `proposal.md`, `design.md`, `tasks.md` e _specs_ por capacidade |

---

## 🗂️ Documentos futuros

Estes artefatos serão adicionados nas fases indicadas:

| Documento | Fase | Conteúdo |
| :-------- | :--: | :------- |
| `docs/API_ERRORS.md` | 8 | Catálogo de erros da API (status HTTP, causas e códigos por módulo) |
| `docs/API_EXAMPLES.md` | 8 | Exemplos `curl` de request/response dos fluxos principais |
| `docs/bounded-contexts.md` | 15 | _Bounded contexts_ e grafo de dependências dos microsserviços |
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
