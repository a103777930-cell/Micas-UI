$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
if (-not $IsWindows -and $env:OS -ne 'Windows_NT') { throw 'Build on Windows.' }
python -m pip install -e '.[desktop,build]'
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
python -m PyInstaller --noconfirm --clean packaging/micas-desktop.spec
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }
Compress-Archive -Path dist/MicasDocumentConverter -DestinationPath dist/MicasDocumentConverter-Windows.zip -Force
