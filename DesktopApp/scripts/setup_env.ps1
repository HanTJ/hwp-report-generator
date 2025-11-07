param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

function Write-Stage {
    param([string]$Message)
    Write-Host ""
    Write-Host "== $Message ==" -ForegroundColor Cyan
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktopAppDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent $desktopAppDir

Set-Location $repoRoot

if (-not (Get-Command $Python -ErrorAction SilentlyContinue)) {
    throw "지정한 Python 실행 파일을 찾을 수 없습니다: $Python"
}

$venvPath = Join-Path $repoRoot ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Stage "가상환경 생성 ($Python -m venv .venv)"
    & $Python "-m" "venv" ".venv"
} else {
    Write-Host "기존 가상환경을 재사용합니다: $venvPath"
}

$venvPython = Join-Path $venvPath "Scripts\\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "가상환경 python 실행 파일을 찾을 수 없습니다: $venvPython"
}

Write-Stage "pip 업데이트"
& $venvPython "-m" "pip" "install" "--upgrade" "pip"

Write-Stage "필수 패키지 설치"
& $venvPython "-m" "pip" "install" "-r" "DesktopApp/requirements.txt"

Write-Stage "환경 검증"
& $venvPython "DesktopApp/scripts/verify_environment.py"

Write-Host ""
Write-Host "== 개발 환경 구성이 완료되었습니다. ==" -ForegroundColor Green
