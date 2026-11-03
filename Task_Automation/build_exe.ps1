$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

python -m compileall -q main.py core ui tests

if ($LASTEXITCODE -ne 0) {
    throw "Python compilation failed."
}

python -m unittest discover -s tests -v

if ($LASTEXITCODE -ne 0) {
    throw "Tests failed. EXE build cancelled."
}

python -m PyInstaller --noconfirm --clean --windowed --onefile --name "TaskAutomationPro" main.py

if ($LASTEXITCODE -ne 0) {
    throw "EXE build failed."
}

Write-Host "BUILD SUCCESSFUL" -ForegroundColor Green
Write-Host "EXE: dist\TaskAutomationPro.exe"
