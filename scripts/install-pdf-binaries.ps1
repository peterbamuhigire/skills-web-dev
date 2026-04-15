# Installs PDF/EPUB system binaries on Windows
# Run in an ELEVATED PowerShell (right-click -> Run as Administrator)
#
# What this installs:
#   - Chocolatey (if missing)         — package manager
#   - poppler                          — gives pdftoppm / pdftotext / pdfinfo (needed by pdf2image, unstructured)
#   - tesseract                        — OCR engine (needed by pytesseract, ocrmypdf)
#   - ghostscript                      — needed by camelot-py, some PDF workflows
#   - pandoc                           — needed by pypandoc for EPUB<->Markdown conversion
#
# After this, agents in future sessions will be able to extract your books
# verbatim instead of writing from general knowledge.

$ErrorActionPreference = 'Stop'

# 1. Require admin
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERROR: Run this script as Administrator." -ForegroundColor Red
    Write-Host "Right-click PowerShell -> Run as Administrator, then re-run."
    exit 1
}

# 2. Install Chocolatey if missing
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Cyan
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    # Reload PATH in this session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
} else {
    Write-Host "Chocolatey already installed: $(choco --version)" -ForegroundColor Green
}

# 3. Install system binaries
$packages = @('poppler', 'tesseract', 'ghostscript', 'pandoc')
foreach ($pkg in $packages) {
    Write-Host "`nInstalling $pkg..." -ForegroundColor Cyan
    choco install $pkg -y --no-progress
}

# 4. Reload PATH so binaries are visible in this session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# 5. Verify
Write-Host "`n=== Verification ===" -ForegroundColor Cyan
$checks = @(
    @{ Name = 'pdftoppm';   Cmd = 'pdftoppm -v' },
    @{ Name = 'pdftotext';  Cmd = 'pdftotext -v' },
    @{ Name = 'tesseract';  Cmd = 'tesseract --version' },
    @{ Name = 'gs';         Cmd = 'gs --version' },
    @{ Name = 'pandoc';     Cmd = 'pandoc --version' }
)
foreach ($c in $checks) {
    try {
        $out = Invoke-Expression "$($c.Cmd)" 2>&1 | Select-Object -First 1
        Write-Host ("  [OK] {0,-12} {1}" -f $c.Name, $out) -ForegroundColor Green
    } catch {
        Write-Host ("  [FAIL] {0,-12} not on PATH" -f $c.Name) -ForegroundColor Red
    }
}

Write-Host "`nDone. Open a NEW terminal so PATH picks up the new binaries." -ForegroundColor Cyan
Write-Host "Test in Python with:"
Write-Host '    python -c "import pdf2image; pdf2image.convert_from_path(''sample.pdf'', first_page=1, last_page=1)"'
