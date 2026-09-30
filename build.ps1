$ErrorActionPreference = "Stop"

# Always build from the repository root, even if the script is launched from another folder.
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Explicitly add the repository root to PyInstaller import paths and collect local packages.
python -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --name SecondBrainAI `
    --paths "$ProjectRoot" `
    --collect-all customtkinter `
    --collect-all easyocr `
    --collect-all sentence_transformers `
    --collect-all torch `
    --collect-all pywinauto `
    --collect-all winsdk `
    --collect-submodules ui `
    --collect-submodules ai `
    --collect-submodules database `
    --collect-submodules memory `
    --collect-submodules services `
    --collect-submodules vision `
    --hidden-import ui.dashboard `
    --hidden-import ui.app_window `
    --hidden-import ui.sidebar `
    --hidden-import memory.recorder `
    app.py

Write-Host "Build complete: dist\SecondBrainAI\SecondBrainAI.exe"

# Release builds are also validated by .github/workflows/windows-build.yml.
