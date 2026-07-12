# 🚨 Catálogo de Erros da API — EnergyHub

Este documento cataloga os **erros** retornados pela API REST do EnergyHub: os **status HTTP**
genéricos e os **códigos de erro** (`error_code`) estáveis e legíveis por máquina emitidos pelas
exceções de domínio. Faz parte da **Fase 8** (documentação da API).

> 📌 Todos os erros seguem um corpo padronizado. Veja também **[API_EXAMPLES.md](./API_EXAMPLES.md)**
> para exemplos `curl` de request/response.

---

## 📦 Formato dos corpos de erro

A API retorna dois formatos, ambos documentados no OpenAPI (`/docs`, `/openapi.json`):

### `ErrorResponse` — erros gerais (`4xx`/`5xx`)

```json
{
  "timestamp": "2026-07-12T12:00:00+00:00",
  "status": 404,
  "error": "Not Found",
  "message": "Cliente 0b1e5b2e-… não encontrado",
  "path": "/api/v1/clients/0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70",
  "error_code": "CLIENT_NOT_FOUND"
}
```

| Campo | Descrição |
| :---- | :-------- |
| `timestamp` | Instante do erro (ISO-8601, UTC). |
| `status` | Código de status HTTP. |
| `error` | Rótulo do tipo de erro (razão HTTP). |
| `message` | Mensagem legível descrevendo a causa. |
| `path` | Caminho da requisição que originou o erro. |
| `error_code` | Código estável e legível por máquina (ver catálogo abaixo); pode ser `null` para erros genéricos. |

### `ValidationErrorResponse` — validação de schema da requisição (`400`)

```json
{
  "status": 400,
  "message": "Erro de validação",
  "errors": [
    { "field": "email", "message": "value is not a valid email address" },
    { "field": "password", "message": "Field required" }
  ]
}
```

Retornado quando o **corpo/parâmetros da requisição** falham na validação do schema (Pydantic).
Traz **um `FieldError` por campo inválido** (`field` + `message`).

---

## 🌐 Status HTTP genéricos

| Status | Significado | Causas comuns |
| :----: | :---------- | :------------ |
| **400** Bad Request | Validação de schema da requisição falhou. | Campo obrigatório ausente, tipo inválido, string fora dos limites (`min_length`/`max_length`), formato inválido. Corpo: `ValidationErrorResponse`. |
| **401** Unauthorized | Não autenticado. | Token JWT ausente, malformado, expirado ou com assinatura inválida; credenciais inválidas no login. Inclui o cabeçalho `WWW-Authenticate: Bearer`. |
| **403** Forbidden | Autenticado, porém sem permissão. | O usuário não possui a permissão exigida pelo endpoint (ex.: `CLIENT_CREATE`). |
| **404** Not Found | Recurso inexistente. | Id que não corresponde a nenhum registro; sub-recurso de um pai inexistente. |
| **409** Conflict | Conflito de estado. | Violação de unicidade (ex.: CNPJ/username/número já cadastrado) ou regra de negócio que impede a operação. |
| **422** Unprocessable Entity | Violação de validação de **domínio**. | Dados sintaticamente válidos mas que violam uma invariante do domínio (ex.: CNPJ inválido, transição de estado ilegal). |
| **500** Internal Server Error | Erro interno inesperado. | Falha não tratada no servidor. A mensagem é genérica (não vaza detalhes internos); `error_code` = `INTERNAL_SERVER_ERROR`. |

> ℹ️ **400 × 422:** `400` é falha de **schema** da requisição (Pydantic, antes de chegar ao domínio);
> `422` é violação de **regra de validação do domínio** (após o parse). São formatos e camadas distintos.

---

## 🔑 Códigos de erro (`error_code`)

Cada exceção de domínio expõe um `error_code` estável — use-o para ramificar o tratamento no
cliente, em vez de depender da `message` (que pode mudar).

### Genéricos (camada compartilhada)

| `error_code` | HTTP | Descrição |
| :----------- | :--: | :-------- |
| `DOMAIN_ERROR` | 422 | Erro de domínio genérico (fallback). |
| `RESOURCE_NOT_FOUND` | 404 | Recurso solicitado não existe (base dos `*_NOT_FOUND`). |
| `VALIDATION_ERROR` | 422 | Violação de validação de domínio (base dos `INVALID_*`). |
| `BUSINESS_RULE_VIOLATION` | 409 | Regra de negócio violada (base dos `*_ALREADY_EXISTS`). |
| `INTERNAL_SERVER_ERROR` | 500 | Erro interno inesperado. |

### Autenticação & Acesso (`auth`)

| `error_code` | HTTP | Descrição |
| :----------- | :--: | :-------- |
| `INVALID_CREDENTIALS` | 401 | Usuário/senha inválidos ou conta inativa no login (não revela qual condição falhou). |
| `USER_NOT_FOUND` | 404 | Usuário não encontrado. |
| `USER_ALREADY_EXISTS` | 409 | Já existe usuário com o mesmo `username`/`email`. |
| `ROLE_NOT_FOUND` | 404 | Papel não encontrado. |
| `ROLE_ALREADY_EXISTS` | 409 | Já existe papel com o mesmo nome. |
| `PERMISSION_NOT_FOUND` | 404 | Permissão não encontrada. |
| `PERMISSION_ALREADY_EXISTS` | 409 | Já existe permissão com o mesmo nome. |

### Clientes (`clients`)

| `error_code` | HTTP | Descrição |
| :----------- | :--: | :-------- |
| `CLIENT_NOT_FOUND` | 404 | Cliente não encontrado. |
| `CLIENT_ALREADY_EXISTS` | 409 | Já existe cliente com o mesmo CNPJ. |
| `INVALID_CNPJ` | 422 | CNPJ inválido (dígitos verificadores ou formato). |
| `INVALID_CLIENT_STATE` | 422 | Operação inválida para o estado atual do cliente. |

### Contratos (`contracts`)

| `error_code` | HTTP | Descrição |
| :----------- | :--: | :-------- |
| `CONTRACT_NOT_FOUND` | 404 | Contrato não encontrado. |
| `CONTRACT_ALREADY_EXISTS` | 409 | Já existe contrato com o mesmo número. |
| `INVALID_CONTRACT_STATUS` | 422 | Transição de estado inválida (ex.: ativar um contrato não aprovado). |

### Negociações (`negotiations`)

| `error_code` | HTTP | Descrição |
| :----------- | :--: | :-------- |
| `NEGOTIATION_NOT_FOUND` | 404 | Negociação não encontrada. |
| `ENERGY_TRANSACTION_NOT_FOUND` | 404 | Transação de energia não encontrada. |
| `INVALID_NEGOTIATION` | 422 | Operação inválida para o estado da negociação. |

### Financeiro (`financial`)

| `error_code` | HTTP | Descrição |
| :----------- | :--: | :-------- |
| `INVOICE_NOT_FOUND` | 404 | Fatura não encontrada. |
| `INVOICE_ALREADY_EXISTS` | 409 | Já existe fatura com o mesmo número. |
| `PAYMENT_NOT_FOUND` | 404 | Pagamento não encontrado. |

### Auditoria · Notificações · Relatórios

| `error_code` | HTTP | Descrição |
| :----------- | :--: | :-------- |
| `AUDIT_LOG_NOT_FOUND` | 404 | Log de auditoria não encontrado. |
| `NOTIFICATION_NOT_FOUND` | 404 | Notificação não encontrada. |
| `REPORT_NOT_FOUND` | 404 | Relatório não encontrado. |

---

<sub>Documento da Fase 8 · mantido junto ao código; os `error_code` vivem nas exceções de domínio
(`<módulo>/domain/exception/`). Voltar ao <a href="./README.md">índice da documentação</a>.</sub>
