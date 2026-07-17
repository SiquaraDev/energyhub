#!/usr/bin/env bash
# Branch protection do EnergyHub — configuração REPRODUTÍVEL (harden-cicd-supply-chain).
#
# Por que um script e não cliques: branch protection vive nas SETTINGS do GitHub, fora dos arquivos
# de workflow — o YAML não consegue se auto-proteger. Deixar isso como "vá lá e marque estas caixas"
# é indocumentável e some no primeiro operador novo. Aqui as regras viram CÓDIGO: versionado,
# revisável em PR, auditável e re-aplicável.
#
# ATENÇÃO — este script MUDA as settings do repositório. Ele NÃO roda sozinho em nenhuma esteira e
# exige confirmação explícita. Requer um token com escopo `repo` e permissão de ADMIN no repo.
#
#   Uso:
#     bash .github/branch-protection.sh                 # mostra o plano (dry-run) e sai
#     bash .github/branch-protection.sh --apply         # aplica (pede confirmação)
#     bash .github/branch-protection.sh --apply --yes   # aplica sem perguntar (automação)
#     bash .github/branch-protection.sh --show          # mostra a proteção vigente
#     bash .github/branch-protection.sh --remove --yes  # REMOVE a proteção (rollback)
#
#   Variáveis:
#     REPO=owner/nome     sobrepõe a detecção automática do repositório
#     ENFORCE_ADMINS=true também sujeita os admins às regras (ver a armadilha abaixo)
#
# ┌─ ARMADILHA DO REPO SOLO ────────────────────────────────────────────────────────────────────┐
# │ O GitHub NÃO deixa você aprovar seu próprio PR. Num repo de um mantenedor só, exigir 1      │
# │ aprovação + ENFORCE_ADMINS=true trava o merge de TUDO: ninguém pode aprovar. Por isso o     │
# │ default aqui é ENFORCE_ADMINS=false — colaboradores passam pelo fluxo completo (PR + review │
# │ + checks) e você, como admin, mantém a válvula de escape. Só ligue ENFORCE_ADMINS=true      │
# │ quando houver um segundo mantenedor capaz de aprovar.                                       │
# └─────────────────────────────────────────────────────────────────────────────────────────────┘
set -euo pipefail

# Checks EXIGIDOS antes de qualquer merge. Estes nomes são o `name` do check run — para um job sem
# `name:`, é o ID do job. `build` vem de build.yml (jobs.build) e `test` de test.yml (jobs.test).
#
# Por que SÓ estes dois, e por que com app_id:
#   • docker.yml também tem um job `build`, mas por ser MATRIZ seus checks saem como
#     "build (auth-service)", ... — não colidem com o `build` puro. Verificado na API, não suposto.
#   • `deploy` está de fora DE PROPÓSITO: deploy.yml e ci-cd.yml expõem DOIS check runs com o mesmo
#     nome `deploy` — exigir esse nome é ambíguo. Além disso, gatear merge em deploy prenderia o PR
#     à disponibilidade de registry/cluster (uma queda do GHCR bloquearia todo merge).
#   • app_id 15368 = GitHub Actions. Fixar o app impede que outra integração qualquer publique um
#     check chamado "build" e satisfaça a exigência por acidente.
REQUIRED_CHECKS_JSON='[{"context":"build","app_id":15368},{"context":"test","app_id":15368}]'

# `master` é o branch default. `main` está aqui porque os workflows honram ambos por portabilidade;
# hoje ele NÃO existe neste repo e será pulado com aviso — proteger branch inexistente dá 404.
BRANCHES=(master main)

ENFORCE_ADMINS="${ENFORCE_ADMINS:-false}"
MODE="plan"
ASSUME_YES="false"

for arg in "$@"; do
  case "$arg" in
    --apply)  MODE="apply" ;;
    --remove) MODE="remove" ;;
    --show)   MODE="show" ;;
    --yes|-y) ASSUME_YES="true" ;;
    -h|--help) sed -n '1,40p' "$0"; exit 0 ;;
    *) echo "ERRO: argumento desconhecido: $arg" >&2; exit 2 ;;
  esac
done

command -v gh >/dev/null 2>&1 || { echo "ERRO: gh CLI nao encontrado (https://cli.github.com)." >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "ERRO: gh nao autenticado. Rode: gh auth login" >&2; exit 1; }

REPO="${REPO:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"
echo "Repositorio: ${REPO}"
echo "Modo:        ${MODE}    enforce_admins=${ENFORCE_ADMINS}"
echo

# Payload da API de proteção. Notas de contrato (a API é exigente):
#   • required_pull_request_reviews NAO-nulo é o que BLOQUEIA PUSH DIRETO — o GitHub passa a exigir
#     que toda mudança chegue por pull request ("Changes must be made through a pull request").
#   • restrictions SÓ funciona em repo de organização; num repo de usuário TEM de ser null, senão a
#     chamada falha.
#   • strict:true = "branch tem de estar atualizado antes do merge" — impede que dois PRs verdes em
#     isolamento quebrem o master ao se encontrarem (semantic conflict). O Dependabot rebaseia os
#     PRs dele sozinho, então o custo aqui é baixo.
#   • allow_force_pushes/allow_deletions false: protege o histórico do master contra reescrita.
protection_payload() {
  cat <<EOF
{
  "required_status_checks": {
    "strict": true,
    "checks": ${REQUIRED_CHECKS_JSON}
  },
  "enforce_admins": ${ENFORCE_ADMINS},
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
EOF
}

branch_exists() {
  gh api "repos/${REPO}/branches/$1" --jq .name >/dev/null 2>&1
}

case "$MODE" in
  show)
    # Usa o --jq EMBUTIDO do gh: um `| jq` externo adicionaria uma dependencia que nem sempre existe
    # (no Git Bash do Windows, tipicamente nao existe) — e, pior, o `|| echo "(sem protecao)"` que
    # havia aqui capturava o "jq: command not found" e reportava "sem protecao" para um branch que
    # ESTAVA protegido. Um falso negativo silencioso num script de seguranca.
    #
    # Cuidado com os TIPOS na resposta do GET (eles nao sao uniformes):
    #   • enforce_admins / allow_force_pushes / allow_deletions -> OBJETO {enabled: bool}
    #   • dismiss_stale_reviews / strict                        -> BOOLEAN direto
    # Trocar um pelo outro faz o jq abortar com "expected an object but got: boolean".
    for b in "${BRANCHES[@]}"; do
      echo "--- ${b}"
      if ! branch_exists "$b"; then echo "    (branch nao existe)"; continue; fi
      if ! gh api "repos/${REPO}/branches/${b}/protection" --jq '
            "    push direto bloqueado : \(.required_pull_request_reviews != null)",
            "    aprovacoes exigidas   : \(.required_pull_request_reviews.required_approving_review_count // 0)",
            "    checks exigidos       : \([.required_status_checks.checks[]?.context] | join(", "))",
            "    strict (up to date)   : \(.required_status_checks.strict)",
            "    enforce_admins        : \(.enforce_admins.enabled)",
            "    force push permitido  : \(.allow_force_pushes.enabled)",
            "    delecao permitida     : \(.allow_deletions.enabled)"
          ' 2>/dev/null; then
        # Distingue "sem protecao" (404 legitimo) de um erro de chamada — antes tudo virava
        # "(sem protecao)", inclusive falha de rede, token sem escopo ou binario ausente.
        if gh api "repos/${REPO}/branches/${b}/protection" 2>&1 | grep -q "Branch not protected"; then
          echo "    (sem protecao)"
        else
          echo "    ERRO ao consultar a protecao (token sem escopo 'repo'? sem rede?):" >&2
          gh api "repos/${REPO}/branches/${b}/protection" 2>&1 | head -2 >&2
        fi
      fi
    done
    exit 0
    ;;

  plan)
    echo "PLANO (nada sera alterado — rode com --apply para aplicar):"
    echo
    for b in "${BRANCHES[@]}"; do
      if branch_exists "$b"; then echo "  [PROTEGER] ${b}"; else echo "  [PULAR]    ${b}  (branch nao existe neste repo)"; fi
    done
    echo
    echo "  Regras a aplicar:"
    echo "    - push direto BLOQUEADO (toda mudanca via pull request)"
    echo "    - >=1 aprovacao obrigatoria (aprovacoes velhas sao descartadas a cada novo push)"
    echo "    - required checks: build, test (GitHub Actions, app 15368) + branch atualizado"
    echo "    - force-push e delecao do branch bloqueados"
    echo "    - enforce_admins=${ENFORCE_ADMINS} (admins $([ "$ENFORCE_ADMINS" = "true" ] && echo "TAMBEM sujeitos" || echo "podem contornar"))"
    echo
    protection_payload
    exit 0
    ;;

  apply)
    if [ "$ASSUME_YES" != "true" ]; then
      echo "Isto vai alterar as settings de ${REPO}."
      [ "$ENFORCE_ADMINS" = "true" ] && echo "AVISO: enforce_admins=true — num repo solo isso pode travar TODOS os merges (ver cabecalho)."
      read -r -p "Confirmar? [y/N] " ans
      [ "$ans" = "y" ] || [ "$ans" = "Y" ] || { echo "Abortado."; exit 1; }
    fi
    rc=0
    for b in "${BRANCHES[@]}"; do
      if ! branch_exists "$b"; then
        echo "PULADO  ${b} — branch nao existe neste repo (nada a proteger)."
        continue
      fi
      if protection_payload | gh api --method PUT "repos/${REPO}/branches/${b}/protection" --input - >/dev/null; then
        echo "OK      ${b} protegido."
      else
        echo "FALHOU  ${b} — o token tem escopo 'repo' e voce e admin do repositorio?" >&2
        rc=1
      fi
    done
    echo
    echo "Confira com: bash .github/branch-protection.sh --show"
    exit "$rc"
    ;;

  remove)
    if [ "$ASSUME_YES" != "true" ]; then
      read -r -p "REMOVER a protecao de ${REPO} (${BRANCHES[*]})? [y/N] " ans
      [ "$ans" = "y" ] || [ "$ans" = "Y" ] || { echo "Abortado."; exit 1; }
    fi
    for b in "${BRANCHES[@]}"; do
      branch_exists "$b" || continue
      gh api --method DELETE "repos/${REPO}/branches/${b}/protection" >/dev/null 2>&1 \
        && echo "OK  protecao removida de ${b}." \
        || echo "--  ${b} ja estava sem protecao."
    done
    exit 0
    ;;
esac
