#!/usr/bin/env bash
# Cria o `ghcr-pull-secret` — credencial que o cluster usa para puxar as imagens PRIVADAS do GHCR
# (harden-cicd-supply-chain).
#
# Por que existe: ghcr.io/siquaradev/energyhub-*-service sao pacotes PRIVADOS (um GET anonimo no
# manifest devolve 401). Num cluster real nao ha `docker login`; sem credencial o kubelet falha o
# pull e os pods ficam em ImagePullBackOff. Este Secret e a credencial; o SA `energyhub-sa`
# (k8s/base/serviceaccount.yaml) o entrega aos 5 servicos.
#
# Por que um SCRIPT e nao um YAML versionado: um `kubernetes.io/dockerconfigjson` embute o TOKEN em
# claro (base64 nao e cifra). Commitar isso repetiria exatamente o erro que a mudanca anterior
# (harden-security-credentials) eliminou ao apagar k8s/secret.yaml. O token so entra pelo ambiente,
# no momento da criacao, e nunca toca o disco do repositorio.
#
#   Uso:
#     export GHCR_USERNAME=SiquaraDev
#     export GHCR_TOKEN=ghp_xxx          # PAT classico com escopo read:packages APENAS
#     bash k8s/secrets/create-ghcr-pull-secret.sh
#
#     bash k8s/secrets/create-ghcr-pull-secret.sh --seal   # gera um SealedSecret cifrado (GitOps)
#
# Sobre o token: use um PAT com read:packages e NADA MAIS — se o cluster for comprometido, o token
# vazado so le imagens. NUNCA use um PAT com write:packages ou repo aqui. Em CI, use o
# GITHUB_TOKEN efemero do proprio run (expira ao fim dele) em vez de um PAT.
set -euo pipefail

NAMESPACE="${NAMESPACE:-energyhub}"
SECRET_NAME="${SECRET_NAME:-ghcr-pull-secret}"
REGISTRY="ghcr.io"
SEAL="false"
[ "${1:-}" = "--seal" ] && SEAL="true"

: "${GHCR_USERNAME:?defina GHCR_USERNAME (ex.: export GHCR_USERNAME=SiquaraDev)}"
: "${GHCR_TOKEN:?defina GHCR_TOKEN (PAT com escopo read:packages — nunca commite este valor)}"

command -v kubectl >/dev/null 2>&1 || { echo "ERRO: kubectl nao encontrado." >&2; exit 1; }

if [ "$SEAL" = "true" ]; then
  command -v kubeseal >/dev/null 2>&1 || { echo "ERRO: kubeseal nao encontrado (ver sealed-secrets-controller.md)." >&2; exit 1; }
  OUT="k8s/secrets/ghcr-pull-sealedsecret.yaml"
  # --dry-run=client -o yaml monta o Secret SEM enviar ao cluster; o pipe entrega direto ao kubeseal,
  # entao o token em claro so existe em memoria — nenhum arquivo intermediario com o segredo.
  kubectl create secret docker-registry "$SECRET_NAME" \
    --namespace "$NAMESPACE" \
    --docker-server="$REGISTRY" \
    --docker-username="$GHCR_USERNAME" \
    --docker-password="$GHCR_TOKEN" \
    --dry-run=client -o yaml \
    | kubeseal --format yaml > "$OUT"
  echo "OK: SealedSecret cifrado gerado em $OUT (seguro para commitar)."
  echo "    Aplique com: kubectl apply -f $OUT"
  exit 0
fi

# --dry-run=client | kubectl apply torna a operacao IDEMPOTENTE: rodar de novo (ex.: para rotacionar
# o token) atualiza o Secret existente. Um `kubectl create secret` puro falharia com AlreadyExists.
kubectl create secret docker-registry "$SECRET_NAME" \
  --namespace "$NAMESPACE" \
  --docker-server="$REGISTRY" \
  --docker-username="$GHCR_USERNAME" \
  --docker-password="$GHCR_TOKEN" \
  --dry-run=client -o yaml \
  | kubectl apply -f -

echo "OK: Secret '$SECRET_NAME' criado/atualizado no namespace '$NAMESPACE'."
echo
echo "Verifique o wiring (deve listar ghcr-pull-secret):"
echo "  kubectl -n $NAMESPACE get serviceaccount energyhub-sa -o jsonpath='{.imagePullSecrets}'"
echo
echo "Apos ROTACIONAR o token, reinicie os pods para revalidar o pull:"
echo "  kubectl -n $NAMESPACE rollout restart deployment -l app.kubernetes.io/part-of=energyhub"
