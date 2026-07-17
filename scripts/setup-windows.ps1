$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

$uv = Get-Command uv -ErrorAction SilentlyContinue
$python = Get-Command py -ErrorAction SilentlyContinue
if ($uv) {
    if (-not (Test-Path .\.venv\Scripts\python.exe)) {
        & uv venv --python 3.12 .venv
        if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o ambiente virtual com uv." }
    }
} elseif ($python) {
    if (-not (Test-Path .\.venv\Scripts\python.exe)) {
        & py -3.12 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o ambiente virtual." }
    }
} else {
    $version = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ($LASTEXITCODE -ne 0) { throw "Python não encontrado." }
    if ($version -ne "3.12" -and $version -ne "3.13") {
        throw "Instale Python 3.12 (recomendado) ou uv antes de continuar."
    }
    if (-not (Test-Path .\.venv\Scripts\python.exe)) {
        & python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o ambiente virtual." }
    }
}

if ($uv) {
    & uv pip install --python .\.venv\Scripts\python.exe -r requirements.lock
    if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar as dependências." }
    & uv pip install --python .\.venv\Scripts\python.exe --no-deps -e .
    if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar o pacote." }
} else {
    & .\.venv\Scripts\python.exe -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "Falha ao atualizar o pip." }
    & .\.venv\Scripts\python.exe -m pip install -r requirements.lock
    if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar as dependências." }
    & .\.venv\Scripts\python.exe -m pip install --no-deps -e .
    if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar o pacote." }
}
New-Item -ItemType Directory -Force entrada, saida | Out-Null

Write-Host ""
Write-Host "Instalação concluída. Para usar:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  livros-md doctor"
