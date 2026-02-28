# One-click build and optional tag for Windows Cleaner release.
# Run from project root: .\scripts\release.ps1
# Requires: Python, Node, frontend already has node_modules (run npm install in frontend once).

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot + "\.."
Push-Location $root

try {
    # Read version from backend
    $constantsPath = Join-Path $root "backend\core\constants.py"
    $content = Get-Content $constantsPath -Raw
    if ($content -match 'APP_VERSION\s*=\s*"([^"]+)"') {
        $ver = $Matches[1]
        Write-Host "Version from constants: $ver"
    } else {
        Write-Host "Could not read APP_VERSION from backend\core\constants.py"
        exit 1
    }

    # Build frontend
    Write-Host "Building frontend..."
    Set-Location (Join-Path $root "frontend")
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
    Set-Location $root

    # Build exe and zip
    Write-Host "Running packaging/build_exe.py --zip..."
    python packaging/build_exe.py --zip
    if ($LASTEXITCODE -ne 0) { throw "Build failed" }

    $zipName = "WindowsCleaner-v$ver-win64.zip"
    $zipPath = Join-Path $root "dist\$zipName"
    if (Test-Path $zipPath) {
        Write-Host "Created: $zipPath"
    } else {
        Write-Host "Warning: Expected zip not found at $zipPath"
    }

    Write-Host ""
    Write-Host "To create a GitHub Release, run:"
    Write-Host "  git tag v$ver"
    Write-Host "  git push origin v$ver"
    Write-Host "Then check Actions and the Releases page."
} finally {
    Pop-Location
}
