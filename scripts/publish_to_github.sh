#!/usr/bin/env bash
set -euo pipefail

# Uso:
#   ./scripts/publish_to_github.sh FrancoEvora/evora-leadflow
#
# Pré-requisito:
#   1. Criar o repositório vazio no GitHub.
#   2. Ter git autenticado no computador.

REPO_FULL_NAME="${1:-}"

if [[ -z "$REPO_FULL_NAME" ]]; then
  echo "Uso: ./scripts/publish_to_github.sh FrancoEvora/evora-leadflow"
  exit 1
fi

if [[ -f .env ]]; then
  echo "Atenção: .env existe localmente, mas está protegido pelo .gitignore e não será enviado."
fi

git init
git branch -M main
git add .
git commit -m "MVP do Évora LeadFlow" || true

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "https://github.com/${REPO_FULL_NAME}.git"
else
  git remote add origin "https://github.com/${REPO_FULL_NAME}.git"
fi

git push -u origin main

echo "Publicado em: https://github.com/${REPO_FULL_NAME}"
