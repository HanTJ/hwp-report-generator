Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot   = (Split-Path -Parent $PSScriptRoot)
Set-Location $PSScriptRoot

$env:PATH_PROJECT_HOME = $RepoRoot

$activate = Join-Path '.venv' 'Scripts' 'Activate.ps1'
if (-not (Test-Path $activate)) { throw 'Run dev_setup.ps1 first to create .venv' }
& $activate

Write-Host 'Starting FastAPI server on http://localhost:8000' -ForegroundColor Cyan
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

