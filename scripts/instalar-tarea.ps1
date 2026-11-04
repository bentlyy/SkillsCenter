# Registra el rastreo diario en el Programador de tareas de Windows.
# Uso: .\scripts\instalar-tarea.ps1 [-Hora "08:00"] [-Nombre "SkillRadarDiario"]
param(
    [string]$Hora = "08:00",
    [string]$Nombre = "SkillRadarDiario"
)

$ErrorActionPreference = "Stop"
$script = Join-Path $PSScriptRoot "radar-diario.ps1"

$accion = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`""

$disparador = New-ScheduledTaskTrigger -Daily -At $Hora
$ajustes = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName $Nombre `
    -Action $accion `
    -Trigger $disparador `
    -Settings $ajustes `
    -Description "Actualiza el catalogo de Skill Radar y genera el informe diario." `
    -Force | Out-Null

Write-Host "Tarea '$Nombre' registrada: todos los dias a las $Hora."
Write-Host "Para quitarla: Unregister-ScheduledTask -TaskName $Nombre"
