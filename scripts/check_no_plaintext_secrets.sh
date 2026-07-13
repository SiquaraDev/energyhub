#!/usr/bin/env bash
# check_no_plaintext_secrets.sh — Guarda de CI contra credenciais em texto puro (harden-security).
#
# Roda no ubuntu-latest do GitHub Actions (só precisa de coreutils + grep/find). Faz DUAS
# verificações independentes; qualquer uma falha o build (exit 1):
#
#   (1) Nenhum Secret do Kubernetes em TEXTO PURO sob k8s/.
#       Um manifesto `kind: Secret` com `stringData:`/`data:` embutido versiona a credencial no
#       git (Secret do k8s é só base64, NÃO é cifra). O padrão aprovado é SealedSecret / ExternalSecret
#       (valores fora do git) — ou, para desenvolvimento, um arquivo `*.example.yaml` com REPLACE_ME.
#       Arquivos `*example*` são PERMITIDOS (usam REPLACE_ME, não segredo real) e ficam de fora.
#
#   (2) Nenhum VALOR placeholder conhecido aparecendo como credencial ATIVA em artefato deployável.
#       Valores proibidos: `change-me-in-production`, `energyhub123` e o par admin/admin do Grafana.
#       Escopo: docker-compose.yml, k8s/, services/, energyhub/src/, energyhub/alembic/.
#       Ficam de fora os locais que MENCIONAM legitimamente essas strings (ver exclusões abaixo).
#
# Uso: bash scripts/check_no_plaintext_secrets.sh   (executar na RAIZ do repositório).

set -uo pipefail

# Cores só quando a saída é um terminal (mantém o log do CI limpo, sem escapes ANSI).
if [ -t 1 ]; then
  RED=$'\033[31m'; GREEN=$'\033[32m'; BOLD=$'\033[1m'; RESET=$'\033[0m'
else
  RED=''; GREEN=''; BOLD=''; RESET=''
fi

# Ancora a execução na raiz do repo (pai deste script) — independe do diretório de onde é chamado.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT" || exit 2

fail=0

# ---------------------------------------------------------------------------
# (1) Secrets do Kubernetes em texto puro sob k8s/
# ---------------------------------------------------------------------------
# Para cada YAML de k8s/ que NÃO seja *example*: é texto puro se tiver a linha EXATA `kind: Secret`
# (o regex ancorado em fim-de-linha NÃO casa `kind: SealedSecret`, `kind: ExternalSecret` nem
# `kind: SecretStore`) E TAMBÉM uma chave `stringData:`/`data:` no início de linha (evita casar
# `metadata:`).
echo "${BOLD}==> (1) Secrets do Kubernetes em texto puro sob k8s/${RESET}"
plaintext_hits=0
if [ -d k8s ]; then
  while IFS= read -r f; do
    if grep -Eq '^[[:space:]]*kind:[[:space:]]*Secret[[:space:]]*$' "$f" \
       && grep -Eq '^[[:space:]]*(stringData|data):' "$f"; then
      echo "${RED}  x Secret em texto puro: $f${RESET}"
      grep -nE '^[[:space:]]*(kind:[[:space:]]*Secret[[:space:]]*$|(stringData|data):)' "$f" \
        | sed 's/^/        /'
      plaintext_hits=$((plaintext_hits + 1))
    fi
  done < <(find k8s -type f \( -name '*.yaml' -o -name '*.yml' \) ! -name '*example*' | sort)
fi
if [ "$plaintext_hits" -gt 0 ]; then
  echo "${RED}  -> Migre para SealedSecret/ExternalSecret ou use um *.example.yaml com REPLACE_ME.${RESET}"
  fail=1
else
  echo "${GREEN}  ok Nenhum Secret em texto puro sob k8s/.${RESET}"
fi

echo

# ---------------------------------------------------------------------------
# (2) Valores placeholder como credencial ativa em artefatos deployáveis
# ---------------------------------------------------------------------------
echo "${BOLD}==> (2) Valores placeholder ativos em artefatos deployáveis${RESET}"

# Escopo de busca: só os caminhos que existem (evita erro do grep com caminho ausente).
SCOPE=()
for p in docker-compose.yml k8s services energyhub/src energyhub/alembic; do
  [ -e "$p" ] && SCOPE+=("$p")
done

# Valores proibidos. `admin/admin` é o par usuário/senha default do Grafana.
PATTERN='change-me-in-production|energyhub123|admin/admin'

# Exclusões — locais que legitimamente MENCIONAM (não USAM) essas strings:
#   -I / --exclude-dir=__pycache__  -> binários .pyc compilados dos config.py;
#   --exclude-dir=tests             -> fixtures/asserts das suítes (*/tests/*);
#   --exclude-dir=openspec          -> documentação de proposta/spec;
#   --exclude=*.md                  -> READMEs/docs;
#   --exclude=.env.example          -> template de ambiente;
#   --exclude=security_guard.py     -> docstring + lista do guard do monólito;
#   --exclude=check_no_plaintext_secrets.sh -> este próprio script;
#   | grep -v KNOWN_PLACEHOLDERS    -> a linha-tuple de detecção dos guards (ex.: _KNOWN_PLACEHOLDERS
#                                      nos config.py dos serviços) contém a substring KNOWN_PLACEHOLDERS.
placeholder_hits=""
if [ "${#SCOPE[@]}" -gt 0 ]; then
  placeholder_hits="$(
    grep -rnIE "$PATTERN" "${SCOPE[@]}" \
      --exclude-dir=__pycache__ \
      --exclude-dir=tests \
      --exclude-dir=openspec \
      --exclude='*.md' \
      --exclude='.env.example' \
      --exclude='security_guard.py' \
      --exclude='check_no_plaintext_secrets.sh' \
      2>/dev/null \
    | grep -v 'KNOWN_PLACEHOLDERS' || true
  )"
fi

if [ -n "$placeholder_hits" ]; then
  echo "${RED}  x Valor placeholder usado como credencial ativa:${RESET}"
  printf '%s\n' "$placeholder_hits" | sed 's/^/        /'
  echo "${RED}  -> Leia de variável de ambiente / secret manager; nunca commite credencial real.${RESET}"
  fail=1
else
  echo "${GREEN}  ok Nenhum valor placeholder ativo no escopo.${RESET}"
fi

echo
if [ "$fail" -ne 0 ]; then
  echo "${RED}${BOLD}FALHOU: credencial em texto puro / placeholder ativo detectado.${RESET}"
  exit 1
fi
echo "${GREEN}${BOLD}OK: nenhum Secret em texto puro nem placeholder ativo detectado.${RESET}"
exit 0
