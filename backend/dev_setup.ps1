param(
  [switch]$StartServer
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host '== HWP Report Generator - Dev Setup (Windows) ==' -ForegroundColor Cyan

# Paths
$RepoRoot   = (Split-Path -Parent $PSScriptRoot)
$BackendDir = Join-Path $RepoRoot 'backend'
Set-Location $BackendDir

# Ensure PATH_PROJECT_HOME for this session
$env:PATH_PROJECT_HOME = $RepoRoot
Write-Host "PATH_PROJECT_HOME=$env:PATH_PROJECT_HOME"

# Python detection
function Get-Python {
  try { return (Get-Command python -ErrorAction Stop).Source } catch {}
  try { return (Get-Command py -ErrorAction Stop).Source } catch {}
  throw 'Python not found. Install Python 3.12+ and retry.'
}

$python = Get-Python
Write-Host "Using Python: $python"

# Create venv if missing
if (-not (Test-Path '.venv')) {
  Write-Host 'Creating virtual environment (.venv)...'
  & $python -m venv .venv
}

# Activate venv
$activate = Join-Path '.venv' 'Scripts' 'Activate.ps1'
if (-not (Test-Path $activate)) { throw 'Activation script not found.' }
& $activate

# Ensure pip is available
try {
  python -m pip -V | Out-Null
} catch {
  Write-Host 'Bootstrapping pip via ensurepip...'
  python -m ensurepip -U
}

# Install requirements
Write-Host 'Installing Python dependencies...'
python -m pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
Write-Host 'Initializing database...'
python init_db.py

Write-Host 'Setup complete.' -ForegroundColor Green

if ($StartServer) {
  Write-Host 'Starting FastAPI dev server on http://localhost:8000 ...'
  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

