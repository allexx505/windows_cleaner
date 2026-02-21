# Start Windows Cleaner API only (no tray, no window).
# Run from project root: .\scripts\run_api_only.ps1
# Or from scripts: ..\run_api_only.ps1 (adjust path to run.py)

$ErrorActionPreference = "Stop"
$Root = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$ProjectRoot = Resolve-Path (Join-Path $Root "..")
$LogDir = Join-Path $env:APPDATA "WindowsCleaner\logs"
$LogPath = Join-Path $LogDir "windows_cleaner.log"
$Url = "http://127.0.0.1:8765"

Write-Host "Starting API only (no tray)."
Write-Host "  URL:    $Url"
Write-Host "  Log:    $LogPath"
Write-Host "  Health: $Url/api/health"
Write-Host ""

Set-Location $ProjectRoot
& python run.py --no-tray
