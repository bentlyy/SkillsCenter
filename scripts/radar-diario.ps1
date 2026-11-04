# Sincroniza el catalogo y genera el informe diario.
# Uso: .\scripts\radar-diario.ps1
$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $repo "src"
$python = if ($env:SKILL_RADAR_PYTHON) { $env:SKILL_RADAR_PYTHON } else { "python" }

$informes = Join-Path $repo "informes"
New-Item -ItemType Directory -Force -Path $informes | Out-Null

$fecha = Get-Date -Format "yyyy-MM-dd"
$destino = Join-Path $informes "digest-$fecha.md"

Write-Host "[skill-radar] sincronizando fuentes..."
& $python -m skill_radar sync
$codigo = $LASTEXITCODE

Write-Host "[skill-radar] generando $destino"
& $python -m skill_radar digest --dias 1 --limite 20 --salida $destino

if ($codigo -ne 0) {
    Write-Host "[skill-radar] alguna fuente fallo; revisa 'skill-radar fuentes'." -ForegroundColor Yellow
}

exit $codigo
