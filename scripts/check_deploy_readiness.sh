#!/usr/bin/env bash
set -euo pipefail

echo "1/4 Limpando caches locais..."
find . -type d -name __pycache__ -prune -exec rm -rf {} +
rm -rf .pytest_cache

echo "2/4 Compilando Python..."
python -m compileall app tests >/dev/null

echo "3/4 Rodando testes..."
pytest -q

echo "4/4 Conferindo arquivos de deploy..."
test -f vercel.json
test -f pyproject.toml
test -f .python-version
test -f .env.example

echo "Pronto para GitHub/Vercel."
