$ErrorActionPreference = "Stop"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
python -m PyInstaller --noconfirm --clean --onedir --name SecondBrainAI --collect-all customtkinter --collect-all easyocr --collect-all sentence_transformers --collect-all torch --collect-all pywinauto --collect-all winsdk app.py
Write-Host "Build complete: dist\SecondBrainAI\SecondBrainAI.exe"
