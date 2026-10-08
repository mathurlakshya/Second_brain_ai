$ErrorActionPreference = "Stop"

# Always build from the repository root, even if the script is launched from another folder.
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

# Validate the ML packages before PyInstaller touches them. A stale/corrupted
# transformers install can otherwise be copied into the executable and fail at
# runtime with "source code string cannot contain null bytes".
python -c "import transformers; import sentence_transformers; print('ML package validation OK')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Repairing transformers/sentence-transformers installation..."

    # If pip's package metadata is corrupted, a normal --force-reinstall can fail
    # while trying to read/uninstall the broken RECORD file. Remove only the two
    # affected package directories and their dist-info metadata, then reinstall.
    python -c "import sysconfig, pathlib, shutil; s=pathlib.Path(sysconfig.get_paths()['purelib']); names=('transformers','sentence_transformers'); [shutil.rmtree(p, ignore_errors=True) for n in names for p in list(s.glob(n)) + list(s.glob(n.replace('_','-') + '-*.dist-info')) + list(s.glob(n + '-*.dist-info'))]"
    if ($LASTEXITCODE -ne 0) { throw "Could not clean the corrupted ML package installation." }

    python -m pip install --no-cache-dir --no-deps transformers sentence-transformers
    if ($LASTEXITCODE -ne 0) { throw "Could not reinstall transformers/sentence-transformers." }

    python -c "import transformers; import sentence_transformers; print('ML package repair OK')"
    if ($LASTEXITCODE -ne 0) { throw "ML package validation still fails after repair." }
}

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
