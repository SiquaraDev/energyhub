# Dashboards do Grafana — EnergyHub (Fase 12)

Dashboards **provisionados** automaticamente (carregados de `/var/lib/grafana/dashboards`):

| Arquivo | Dashboard | Painéis |
| :------ | :-------- | :------ |
| `application.json` | EnergyHub · Aplicação | throughput, latência p50/p95/p99, taxa de erro 5xx, recursos do processo Python |
| `business.json` | EnergyHub · Negócio | clientes ativos, clientes criados, faturas pagas, contratos por status |
| `infrastructure.json` | EnergyHub · Infraestrutura | memória/CPU/disco do host, latência p95 da busca (proxy do Elasticsearch) |

## Dashboards da comunidade (import manual)

Dois dashboards da comunidade complementam os acima. Como o import depende de acesso à
grafana.com, faça-o pela UI (**Dashboards → New → Import → informe o ID → selecione o data source
`Prometheus`**):

| ID | Dashboard | Cobertura |
| :- | :-------- | :-------- |
| **14314** | FastAPI Observability | métricas HTTP do `prometheus-fastapi-instrumentator` |
| **10991** | Python / process metrics | GC, threads, file descriptors e recursos do processo Python |

> As credenciais padrão do Grafana (`admin`/`admin`) são **placeholders** — troque antes de qualquer
> uso compartilhado ou de produção.
