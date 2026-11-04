# Sincroniza el catalogo y genera el informe diario.
# Uso: .\scripts\radar-diario.ps1
$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $repo "src"
$python = if ($env:SKILLSCENTER_PYTHON) { $env:SKILLSCENTER_PYTHON } else { "python" }

$informes = Join-Path $repo "informes"
New-Item -ItemType Directory -Force -Path $informes | Out-Null

$fecha = Get-Date -Format "yyyy-MM-dd"
$destino = Join-Path $informes "digest-$fecha.md"

Write-Host "[skillscenter] sincronizando fuentes..."
& $python -m skillscenter sync
$codigo = $LASTEXITCODE

Write-Host "[skillscenter] generando $destino"
& $python -m skillscenter digest --dias 1 --limite 20 --salida $destino

if ($codigo -ne 0) {
    Write-Host "[skillscenter] alguna fuente fallo; revisa 'skillscenter fuentes'." -ForegroundColor Yellow
}

exit $codigo
