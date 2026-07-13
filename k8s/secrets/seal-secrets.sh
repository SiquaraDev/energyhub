#!/usr/bin/env bash
# seal-secrets.sh — cifra o Secret preenchido em um SealedSecret commitável (harden-security).
#
# Fluxo: lê k8s/secrets/energyhub-secret.local.yaml (UNSEALED, gitignored) e usa `kubeseal` para
# produzir k8s/secrets/energyhub-sealedsecret.yaml (CIFRADO, seguro para commitar). Só o controlador
# Sealed Secrets — que guarda a chave privada dentro do cluster — consegue decifrá-lo, gerando o
# Secret `energyhub-secret` no namespace `energyhub`.
#
# Pré-requisitos:
#   • `kubeseal` instalado (mesma minor do controlador — ver sealed-secrets-controller.md).
#   • `kubectl` apontando para o cluster ONDE o controlador Sealed Secrets está instalado
#     (o kubeseal busca a chave PÚBLICA do controlador; sem cluster, use --cert com o cert exportado).
#   • O arquivo preenchido k8s/secrets/energyhub-secret.local.yaml (copie do .example e edite).
set -euo pipefail

# Resolve caminhos relativos a este script (funciona de qualquer diretório).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNSEALED="${SCRIPT_DIR}/energyhub-secret.local.yaml"
SEALED="${SCRIPT_DIR}/energyhub-sealedsecret.yaml"

# Namespace/escopo do Sealed Secrets controller (padrão do projeto).
CONTROLLER_NS="${CONTROLLER_NS:-kube-system}"
CONTROLLER_NAME="${CONTROLLER_NAME:-sealed-secrets-controller}"

if ! command -v kubeseal >/dev/null 2>&1; then
  echo "ERRO: 'kubeseal' não encontrado no PATH. Veja k8s/secrets/sealed-secrets-controller.md." >&2
  exit 1
fi

if [[ ! -f "${UNSEALED}" ]]; then
  echo "ERRO: ${UNSEALED} não existe." >&2
  echo "      Copie o template e preencha os valores:" >&2
  echo "      cp ${SCRIPT_DIR}/energyhub-secret.local.example.yaml ${UNSEALED}" >&2
  exit 1
fi

# Guarda-corpo: recusa selar um arquivo que ainda contém placeholders (evita segredo inválido).
if grep -q "REPLACE_ME" "${UNSEALED}"; then
  echo "ERRO: ${UNSEALED} ainda contém placeholders REPLACE_ME_*. Preencha os valores reais antes de selar." >&2
  exit 1
fi

echo "Selando ${UNSEALED} → ${SEALED} ..."
# --scope strict (padrão): o SealedSecret fica atrelado a namespace+name (energyhub/energyhub-secret).
# --format yaml: saída legível/versionável. O kubeseal busca o cert público via controlador no cluster.
kubeseal \
  --controller-namespace "${CONTROLLER_NS}" \
  --controller-name "${CONTROLLER_NAME}" \
  --scope strict \
  --format yaml \
  < "${UNSEALED}" \
  > "${SEALED}"

echo "OK: ${SEALED} gerado (cifrado, seguro para commitar)."
echo "Aplique com: kubectl apply -f ${SEALED}"
