#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

USE_UV=0

if command -v uv >/dev/null 2>&1; then
  USE_UV=1
  if [[ ! -x .venv/bin/python ]]; then
    uv venv --python 3.12 .venv
  fi
  PYTHON_BIN=".venv/bin/python"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="python3.12"
elif command -v brew >/dev/null 2>&1; then
  echo "Python 3.12 não encontrado. Instalando com Homebrew..."
  brew install python@3.12
  PYTHON_BIN="$(brew --prefix python@3.12)/bin/python3.12"
else
  echo "Falta o Python 3.12 e o Homebrew não está instalado."
  echo "Instale o Homebrew em https://brew.sh e execute este script novamente."
  exit 1
fi

if [[ "$USE_UV" -eq 0 && ! -x .venv/bin/python ]]; then
  "$PYTHON_BIN" -m venv .venv
fi
source .venv/bin/activate
if [[ "$USE_UV" -eq 1 ]]; then
  uv pip install --python .venv/bin/python -r requirements.lock
  uv pip install --python .venv/bin/python --no-deps -e .
else
  python -m pip install --upgrade pip
  python -m pip install -r requirements.lock
  python -m pip install --no-deps -e .
fi

mkdir -p entrada saida

echo
echo "Instalação concluída. Para usar:"
echo "  source .venv/bin/activate"
echo "  livros-md doctor"
