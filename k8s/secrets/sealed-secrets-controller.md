# 🛡️ Controlador Sealed Secrets — versão fixada e instalação

O fluxo padrão (`seal-secrets.sh` + `energyhub-sealedsecret.yaml`) depende do controlador
**Bitnami Sealed Secrets** rodando no cluster. Ele guarda o par de chaves e decifra os
`SealedSecret`s em `Secret`s nativos, dentro do cluster.

## Versão fixada

- **Controlador / CRD:** `v0.27.1`
- **CLI `kubeseal`:** use a **mesma minor** do controlador (`v0.27.1`) para compatibilidade de formato.

> Fixe a versão (evite `latest`) para builds reprodutíveis — mesma disciplina das tags de imagem.

## Instalar o controlador

```bash
# Manifesto oficial da release fixada (instala em kube-system):
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.27.1/controller.yaml

# — ou via Helm —
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm install sealed-secrets sealed-secrets/sealed-secrets \
  --namespace kube-system \
  --version 2.16.1        # chart que empacota o controlador v0.27.1
```

## Instalar o CLI `kubeseal` (v0.27.1)

```bash
# Linux amd64 (ajuste OS/arch conforme necessário):
curl -sSLf -o kubeseal.tar.gz \
  https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.27.1/kubeseal-0.27.1-linux-amd64.tar.gz
tar -xzf kubeseal.tar.gz kubeseal
sudo install -m 0755 kubeseal /usr/local/bin/kubeseal
kubeseal --version   # deve reportar 0.27.1
```

## Verificar

```bash
kubectl get pods -n kube-system -l name=sealed-secrets-controller
# Após pronto, k8s/secrets/seal-secrets.sh consegue buscar o cert público e selar o Secret.
```

> Backup da chave privada do controlador (`kubectl get secret -n kube-system -l
> sealedsecrets.bitnami.com/sealed-secrets-key -o yaml`) é o que permite decifrar em um cluster
> recriado — guarde-o em local seguro, **fora do git**.
