"""Catálogo canônico de permissões RBAC (nomes `<RECURSO>_<AÇÃO>`) — Fase 7.

Fonte única dos nomes consumidos pelos guards `require_permission(...)` nos routers. Mantido em
sincronia com a migração `0009`, que semeia exatamente estas permissões e concede **todas** ao
papel `ADMIN`. Sub-recursos (contatos, transações, pagamentos) reutilizam a permissão do recurso
pai; `audit-logs` é append-only (apenas CREATE/READ).
"""

from __future__ import annotations

# --- Usuários (já semeados na 0008) ---
USER_CREATE = "USER_CREATE"
USER_READ = "USER_READ"
USER_UPDATE = "USER_UPDATE"
USER_DELETE = "USER_DELETE"

# --- Papéis ---
ROLE_CREATE = "ROLE_CREATE"
ROLE_READ = "ROLE_READ"
ROLE_UPDATE = "ROLE_UPDATE"
ROLE_DELETE = "ROLE_DELETE"

# --- Permissões ---
PERMISSION_CREATE = "PERMISSION_CREATE"
PERMISSION_READ = "PERMISSION_READ"
PERMISSION_UPDATE = "PERMISSION_UPDATE"
PERMISSION_DELETE = "PERMISSION_DELETE"

# --- Clientes (contatos reutilizam CLIENT_*) ---
CLIENT_CREATE = "CLIENT_CREATE"
CLIENT_READ = "CLIENT_READ"
CLIENT_UPDATE = "CLIENT_UPDATE"
CLIENT_DELETE = "CLIENT_DELETE"

# --- Contratos ---
CONTRACT_CREATE = "CONTRACT_CREATE"
CONTRACT_READ = "CONTRACT_READ"
CONTRACT_UPDATE = "CONTRACT_UPDATE"
CONTRACT_DELETE = "CONTRACT_DELETE"

# --- Negociações (transações reutilizam NEGOTIATION_*) ---
NEGOTIATION_CREATE = "NEGOTIATION_CREATE"
NEGOTIATION_READ = "NEGOTIATION_READ"
NEGOTIATION_UPDATE = "NEGOTIATION_UPDATE"
NEGOTIATION_DELETE = "NEGOTIATION_DELETE"

# --- Faturas (pagamentos reutilizam INVOICE_*) ---
INVOICE_CREATE = "INVOICE_CREATE"
INVOICE_READ = "INVOICE_READ"
INVOICE_UPDATE = "INVOICE_UPDATE"
INVOICE_DELETE = "INVOICE_DELETE"

# --- Logs de auditoria (append-only) ---
AUDIT_LOG_CREATE = "AUDIT_LOG_CREATE"
AUDIT_LOG_READ = "AUDIT_LOG_READ"

# --- Notificações ---
NOTIFICATION_CREATE = "NOTIFICATION_CREATE"
NOTIFICATION_READ = "NOTIFICATION_READ"
NOTIFICATION_UPDATE = "NOTIFICATION_UPDATE"
NOTIFICATION_DELETE = "NOTIFICATION_DELETE"

# --- Relatórios ---
REPORT_CREATE = "REPORT_CREATE"
REPORT_READ = "REPORT_READ"
REPORT_UPDATE = "REPORT_UPDATE"
REPORT_DELETE = "REPORT_DELETE"

# Catálogo completo (name, description) — espelha a migração 0009. Útil para introspecção/testes.
PERMISSION_CATALOG: list[tuple[str, str]] = [
    (USER_CREATE, "Criar usuários"),
    (USER_READ, "Ler usuários"),
    (USER_UPDATE, "Atualizar usuários"),
    (USER_DELETE, "Remover usuários"),
    (ROLE_CREATE, "Criar papéis"),
    (ROLE_READ, "Ler papéis"),
    (ROLE_UPDATE, "Atualizar papéis"),
    (ROLE_DELETE, "Remover papéis"),
    (PERMISSION_CREATE, "Criar permissões"),
    (PERMISSION_READ, "Ler permissões"),
    (PERMISSION_UPDATE, "Atualizar permissões"),
    (PERMISSION_DELETE, "Remover permissões"),
    (CLIENT_CREATE, "Criar clientes"),
    (CLIENT_READ, "Ler clientes"),
    (CLIENT_UPDATE, "Atualizar clientes"),
    (CLIENT_DELETE, "Remover clientes"),
    (CONTRACT_CREATE, "Criar contratos"),
    (CONTRACT_READ, "Ler contratos"),
    (CONTRACT_UPDATE, "Atualizar contratos"),
    (CONTRACT_DELETE, "Remover contratos"),
    (NEGOTIATION_CREATE, "Criar negociações"),
    (NEGOTIATION_READ, "Ler negociações"),
    (NEGOTIATION_UPDATE, "Atualizar negociações"),
    (NEGOTIATION_DELETE, "Remover negociações"),
    (INVOICE_CREATE, "Criar faturas"),
    (INVOICE_READ, "Ler faturas"),
    (INVOICE_UPDATE, "Atualizar faturas"),
    (INVOICE_DELETE, "Remover faturas"),
    (AUDIT_LOG_CREATE, "Registrar logs de auditoria"),
    (AUDIT_LOG_READ, "Ler logs de auditoria"),
    (NOTIFICATION_CREATE, "Criar notificações"),
    (NOTIFICATION_READ, "Ler notificações"),
    (NOTIFICATION_UPDATE, "Atualizar notificações"),
    (NOTIFICATION_DELETE, "Remover notificações"),
    (REPORT_CREATE, "Criar relatórios"),
    (REPORT_READ, "Ler relatórios"),
    (REPORT_UPDATE, "Atualizar relatórios"),
    (REPORT_DELETE, "Remover relatórios"),
]
