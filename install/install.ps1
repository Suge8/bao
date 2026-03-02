$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$UvInstallUrl = "https://astral.sh/uv/install.ps1"
$MinPython = "3.11"

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message"
}

function Write-Ok {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Fail {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    exit 1
}

function Has-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Ensure-Windows {
    if (-not $env:OS -or $env:OS -ne "Windows_NT") {
        Fail "This script is for Windows only. / This script supports Windows only."
    }
}

function Ensure-Uv {
    if (Has-Command "uv") {
        Write-Ok "uv is already installed. / uv already available."
        return
    }

    Write-Info "Installing uv... / Installing uv..."
    try {
        irm $UvInstallUrl | iex
    }
    catch {
        Fail "Failed to install uv. / uv installation failed."
    }

    $LocalBin = Join-Path $HOME ".local\bin"
    if (Test-Path $LocalBin) {
        $env:Path = "$LocalBin;$env:Path"
    }

    if (-not (Has-Command "uv")) {
        Fail "uv not found after install. / uv not found in PATH after install."
    }

    Write-Ok "uv installed. / uv installed successfully."
}

function Ensure-Python {
    Write-Info "Installing Python $MinPython via uv... / Installing Python $MinPython with uv..."
    try {
        uv python install $MinPython
    }
    catch {
        Fail "Python installation failed. / Failed to install Python $MinPython."
    }
    Write-Ok "Python is ready. / Python installed or already available."
}

function Install-Bao {
    Write-Info "Installing bao-ai from PyPI... / Installing bao-ai from PyPI..."
    try {
        uv tool install --upgrade bao-ai
    }
    catch {
        Fail "Failed to install bao-ai. / bao-ai install failed."
    }

    Write-Info "Verifying installation... / Verifying installation..."
    try {
        uvx --from bao-ai bao --version | Out-Null
    }
    catch {
        Fail "bao command verification failed. / Failed to verify bao command."
    }
    Write-Ok "bao-ai installed successfully. / bao-ai installed successfully."
}

function Print-Finish {
    Write-Host ""
    Write-Ok "All done. Run: bao"
    if (-not (Has-Command "bao")) {
        Write-Info "If 'bao' is not found, open a new terminal or add this path:"
        Write-Info "$HOME\.local\bin"
    }
}

Write-Info "Bao one-click installer (Windows) / Bao one-click installer (Windows)"
Ensure-Windows
Ensure-Uv
Ensure-Python
Install-Bao
Print-Finish
