# 一键重新打包：先构建前端，再打 exe 和 zip。在项目根目录执行: .\packaging\rebuild.ps1
# 若终端未识别 npm，会先刷新 PATH（从系统与用户环境变量读取）。

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path $root)) { $root = (Get-Location).Path }

# 刷新 PATH，确保能找到 npm 和 py
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

Set-Location $root

Write-Host "Building frontend..."
Set-Location "$root\frontend"
npm install 2>$null
if ($LASTEXITCODE -ne 0) { npm install }
npm run build
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "Packaging exe..."
Set-Location $root
py packaging/build_exe.py --zip
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "Done. Output: $root\dist\WindowsCleaner, zip in $root\dist\"
