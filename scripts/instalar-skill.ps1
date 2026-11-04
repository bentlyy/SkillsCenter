# Instala la skill skill-finder en la carpeta de skills del agente.
# Uso:
#   .\scripts\instalar-skill.ps1                 # Claude + Codex + opencode
#   .\scripts\instalar-skill.ps1 -Destino codex
#   .\scripts\instalar-skill.ps1 -Destino opencode
#   .\scripts\instalar-skill.ps1 -Destino claude

param(
    [ValidateSet("opencode", "claude", "codex", "all")]
    [string]$Destino = "all"
)

$ErrorActionPreference = "Stop"

$origen = Join-Path $PSScriptRoot "..\skills\skill-finder"
$origen = (Resolve-Path -LiteralPath $origen).Path

if (-not (Test-Path -LiteralPath (Join-Path $origen "SKILL.md"))) {
    throw "No se encontro SKILL.md en $origen"
}

$catalogo = Join-Path $PSScriptRoot "..\web\assets\catalogo.js"
$destinos = @()
if ($Destino -in @("opencode", "all")) {
    $destinos += @{
        Agente = "opencode"
        Ruta = Join-Path $env:USERPROFILE ".config\opencode\skills\skill-finder"
    }
}
if ($Destino -in @("codex", "all")) {
    $destinos += @{
        Agente = "codex"
        Ruta = Join-Path $env:USERPROFILE ".agents\skills\skill-finder"
    }
}
if ($Destino -in @("claude", "all")) {
    $destinos += @{
        Agente = "claude"
        Ruta = Join-Path $env:USERPROFILE ".claude\skills\skill-finder"
    }
}

$instaladas = @()
foreach ($itemDestino in $destinos) {
    $rutaDestino = $itemDestino.Ruta
    $padre = Split-Path -Parent $rutaDestino
    if (-not (Test-Path -LiteralPath $padre)) {
        New-Item -ItemType Directory -Path $padre -Force | Out-Null
    }
    if (Test-Path -LiteralPath $rutaDestino) {
        Remove-Item -LiteralPath $rutaDestino -Recurse -Force
    }
    Copy-Item -LiteralPath $origen -Destination $rutaDestino -Recurse -Force
    if (Test-Path -LiteralPath $catalogo) {
        $assets = Join-Path $rutaDestino "assets"
        if (-not (Test-Path -LiteralPath $assets)) {
            New-Item -ItemType Directory -Path $assets -Force | Out-Null
        }
        Copy-Item -LiteralPath $catalogo -Destination (Join-Path $assets "catalogo.js") -Force
    }
    $instaladas += [pscustomobject]@{ Agente = $itemDestino.Agente; Ruta = $rutaDestino }
}

if (-not (Test-Path -LiteralPath $catalogo)) {
    Write-Warning "No se encontro $catalogo; la skill necesitara MCP o SQLite."
}

Write-Output "Skill Finder instalada:"
foreach ($item in $instaladas) {
    Write-Output ("  {0,-9} -> {1}" -f $item.Agente, $item.Ruta)
}
Write-Output ""
Write-Output "Reinicia el agente para que descubra la skill."
Write-Output ("Prueba: python `"{0}`" --stats" -f (Join-Path $instaladas[0].Ruta "scripts\skill_finder.py"))
