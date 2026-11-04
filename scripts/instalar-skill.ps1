# Instala la skill skill-finder en la carpeta de skills del agente.
# Uso:
#   .\scripts\instalar-skill.ps1                 # opencode + claude
#   .\scripts\instalar-skill.ps1 -Destino opencode
#   .\scripts\instalar-skill.ps1 -Destino claude

param(
    [ValidateSet("opencode", "claude", "all")]
    [string]$Destino = "all"
)

$ErrorActionPreference = "Stop"

$origen = Join-Path $PSScriptRoot "..\skills\skill-finder"
$origen = (Resolve-Path -LiteralPath $origen).Path

if (-not (Test-Path -LiteralPath (Join-Path $origen "SKILL.md"))) {
    throw "No se encontro SKILL.md en $origen"
}

$destinos = @()
if ($Destino -in @("opencode", "all")) {
    $destinos += Join-Path $env:USERPROFILE ".config\opencode\skills\skill-finder"
}
if ($Destino -in @("claude", "all")) {
    $destinos += Join-Path $env:USERPROFILE ".claude\skills\skill-finder"
}

foreach ($rutaDestino in $destinos) {
    $padre = Split-Path -Parent $rutaDestino
    if (-not (Test-Path -LiteralPath $padre)) {
        New-Item -ItemType Directory -Path $padre -Force | Out-Null
    }
    if (Test-Path -LiteralPath $rutaDestino) {
        Remove-Item -LiteralPath $rutaDestino -Recurse -Force
    }
    Copy-Item -LiteralPath $origen -Destination $rutaDestino -Recurse -Force
    $catalogo = Join-Path $PSScriptRoot "..\landings\assets\catalogo.js"
    if (Test-Path -LiteralPath $catalogo) {
        $assets = Join-Path $rutaDestino "assets"
        if (-not (Test-Path -LiteralPath $assets)) {
            New-Item -ItemType Directory -Path $assets -Force | Out-Null
        }
        Copy-Item -LiteralPath $catalogo -Destination (Join-Path $assets "catalogo.js") -Force
    }
    Write-Output "Skill instalada en $rutaDestino"
}

Write-Output ""
Write-Output "Reinicia el agente para que descubra la skill."
Write-Output "Verifica con: python `"$origen\scripts\skill_finder.py`" --stats"
