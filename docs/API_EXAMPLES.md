# 🧪 Exemplos de Uso da API — EnergyHub

Exemplos `curl` copiáveis dos principais fluxos da API REST do EnergyHub (**Fase 8**). Todos os
endpoints de recurso são **protegidos**: primeiro faça **login** para obter um token JWT e envie-o
no cabeçalho `Authorization: Bearer <TOKEN>`.

> Base URL local: `http://localhost:8000`. Documentação interativa em
> **[`/docs`](http://localhost:8000/docs)** (Swagger UI) e **[`/redoc`](http://localhost:8000/redoc)**.
> Catálogo de erros em **[API_ERRORS.md](./API_ERRORS.md)**.

---

## 1. 🔑 Autenticação (login)

Troca `username`/`password` por um token JWT. **Rota pública** (não exige token).

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "ChangeMe123!"}'
```

**Resposta `200 OK`:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc4Mzg3OTMwMn0.DLyo9JTaDQe0ljDF-zBoGo4nWQZNbtNUIQw99YiLhvQ",
  "token_type": "bearer",
  "user": {
    "id": "00000000-0000-0000-0000-000000000001",
    "username": "admin",
    "email": "admin@energyhub.local",
    "full_name": "Administrador",
    "active": true,
    "roles": [{ "id": "11111111-1111-1111-1111-111111111111", "name": "ADMIN", "permissions": [] }]
  }
}
```

> ⚠️ O usuário `admin` e a senha `ChangeMe123!` são **credenciais de bootstrap** — rotacione-as
> (e o `SECRET_KEY`) antes de qualquer uso real. Credenciais inválidas retornam **401**
> (`error_code: INVALID_CREDENTIALS`).

Guarde o token numa variável de ambiente para reutilizar nos próximos comandos:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "ChangeMe123!"}' | jq -r .access_token)
```

---

## 2. 🏢 Clientes (create · list · get)

Todas as chamadas abaixo exigem `Authorization: Bearer $TOKEN` e a permissão adequada
(`CLIENT_CREATE`, `CLIENT_READ`).

### 2.1 Criar um cliente — `POST /api/v1/clients`

```bash
curl -X POST http://localhost:8000/api/v1/clients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "cnpj": "11222333000181",
        "corporate_name": "Usina Solar Alpha Ltda",
        "trade_name": "Alpha Energia",
        "email": "contato@usina-alpha.example",
        "city": "São Paulo",
        "state": "SP"
      }'
```

**Resposta `201 Created`:**

```json
{
  "id": "0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70",
  "created_at": "2026-07-12T12:00:00Z",
  "updated_at": "2026-07-12T12:00:00Z",
  "cnpj": "11222333000181",
  "corporate_name": "Usina Solar Alpha Ltda",
  "trade_name": "Alpha Energia",
  "email": "contato@usina-alpha.example",
  "city": "São Paulo",
  "state": "SP",
  "active": true,
  "contacts": []
}
```

> Erros possíveis: **400** (validação de schema — ver `ValidationErrorResponse`), **409**
> (`CLIENT_ALREADY_EXISTS` — CNPJ já cadastrado), **422** (`INVALID_CNPJ`).

### 2.2 Listar clientes (paginado) — `GET /api/v1/clients`

```bash
curl -X GET "http://localhost:8000/api/v1/clients?page=0&size=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta `200 OK`:**

```json
{
  "content": [
    {
      "id": "0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70",
      "cnpj": "11222333000181",
      "corporate_name": "Usina Solar Alpha Ltda",
      "active": true,
      "contacts": []
    }
  ],
  "page": 0,
  "size": 20,
  "total_elements": 1,
  "total_pages": 1,
  "first": true,
  "last": true
}
```

Parâmetros de query: `page` (zero-based, `≥ 0`), `size` (`1`–`100`), `sort` (campo), `direction`
(`asc`/`desc`).

### 2.3 Buscar um cliente por id — `GET /api/v1/clients/{id}`

```bash
curl -X GET http://localhost:8000/api/v1/clients/0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70 \
  -H "Authorization: Bearer $TOKEN"
```

Retorna `200 OK` com o `ClientResponseDTO` (mesma forma do item de `content` acima) ou **404**
(`CLIENT_NOT_FOUND`) se o id não existir.

---

## 3. 🔒 Chamando endpoints protegidos

Toda rota de recurso exige o cabeçalho `Authorization: Bearer <TOKEN>`:

```bash
curl -X GET http://localhost:8000/api/v1/contracts \
  -H "Authorization: Bearer $TOKEN"
```

- **Sem** o cabeçalho (ou token inválido/expirado) → **401 Unauthorized**.
- Com token válido, **sem** a permissão exigida pelo endpoint → **403 Forbidden**
  (ex.: `{"detail": "Permissão negada: requer 'CONTRACT_READ'"}`).

> O botão **Authorize** do Swagger UI (`/docs`) usa o esquema `bearerAuth`: cole o token e todas as
> chamadas "Try it out" passam a incluir o cabeçalho automaticamente.

---

<sub>Documento da Fase 8. Voltar ao <a href="./README.md">índice da documentação</a>.</sub>
