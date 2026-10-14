$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

# Validate and repair the complete Hugging Face stack used by local embeddings.
python -c "import transformers; import sentence_transformers; import huggingface_hub; print('ML package validation OK')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Repairing the transformers / sentence-transformers dependency stack..."
    python -c "import sysconfig, pathlib, shutil; s=pathlib.Path(sysconfig.get_paths()['purelib']); names=('transformers','sentence_transformers','huggingface_hub','tokenizers','safetensors'); [shutil.rmtree(p, ignore_errors=True) for n in names for p in list(s.glob(n)) + list(s.glob(n.replace('_','-') + '-*.dist-info')) + list(s.glob(n + '-*.dist-info'))]"
    if ($LASTEXITCODE -ne 0) { throw "Could not clean the corrupted ML dependency installation." }
    python -m pip install --no-cache-dir --upgrade sentence-transformers transformers huggingface-hub tokenizers safetensors
    if ($LASTEXITCODE -ne 0) { throw "Could not reinstall the ML dependency stack." }
    python -c "import transformers; import sentence_transformers; import huggingface_hub; print('ML package repair OK')"
    if ($LASTEXITCODE -ne 0) { throw "ML package validation still fails after repair." }
}

if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

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