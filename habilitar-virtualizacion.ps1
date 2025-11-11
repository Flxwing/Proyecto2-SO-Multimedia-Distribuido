# Script para Habilitar Virtualización en Windows
# EJECUTAR COMO ADMINISTRADOR

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Habilitando Virtualización para Docker Desktop  " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si se ejecuta como Admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ ERROR: Este script debe ejecutarse como Administrador" -ForegroundColor Red
    Write-Host ""
    Write-Host "Pasos:" -ForegroundColor Yellow
    Write-Host "1. Click derecho en PowerShell" -ForegroundColor White
    Write-Host "2. Selecciona 'Ejecutar como administrador'" -ForegroundColor White
    Write-Host "3. Ejecuta de nuevo: .\habilitar-virtualizacion.ps1" -ForegroundColor White
    exit 1
}

Write-Host "✓ Ejecutando como Administrador" -ForegroundColor Green
Write-Host ""

# Opción 1: Habilitar Hyper-V (Windows Pro/Enterprise)
Write-Host "Intentando habilitar Hyper-V..." -ForegroundColor Yellow
try {
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All -NoRestart
    Write-Host "✓ Hyper-V habilitado" -ForegroundColor Green
} catch {
    Write-Host "⚠ No se pudo habilitar Hyper-V (puede que tengas Windows Home)" -ForegroundColor Yellow
}

# Opción 2: Habilitar Plataforma de Máquina Virtual
Write-Host "Habilitando Plataforma de Máquina Virtual..." -ForegroundColor Yellow
try {
    Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart
    Write-Host "✓ Plataforma de Máquina Virtual habilitada" -ForegroundColor Green
} catch {
    Write-Host "✗ Error habilitando Plataforma de Máquina Virtual" -ForegroundColor Red
}

# Opción 3: Habilitar WSL 2
Write-Host "Habilitando WSL (Windows Subsystem for Linux)..." -ForegroundColor Yellow
try {
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart
    Write-Host "✓ WSL habilitado" -ForegroundColor Green
} catch {
    Write-Host "✗ Error habilitando WSL" -ForegroundColor Red
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "  ✓ Proceso completado" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Yellow
Write-Host "1. Debes REINICIAR tu computadora ahora" -ForegroundColor White
Write-Host "2. Después de reiniciar, abre Docker Desktop" -ForegroundColor White
Write-Host "3. Docker debería funcionar correctamente" -ForegroundColor White
Write-Host ""
Write-Host "¿Deseas reiniciar ahora? (S/N): " -ForegroundColor Cyan -NoNewline
$respuesta = Read-Host

if ($respuesta -eq "S" -or $respuesta -eq "s") {
    Write-Host "Reiniciando en 10 segundos..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    Restart-Computer -Force
} else {
    Write-Host "Recuerda reiniciar manualmente para aplicar los cambios" -ForegroundColor Yellow
}
