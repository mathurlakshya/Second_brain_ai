# Second Brain AI

Second Brain AI is a Windows desktop second-brain application that records local computer context, builds searchable memories, and provides optional Gemini-powered intelligence.

## Architecture

### Local by default
- Screen-change detection
- Active application/window tracking
- Windows idle detection
- Accessibility/UI Automation extraction
- OCR fallback
- Local SQLite memory storage
- Local SentenceTransformer embeddings
- Semantic search
- Activity-based memory deduplication: changed screens enrich one ongoing activity record instead of creating a memory per screenshot
- Activity start/end timestamps, including updates while the screen is static
- Thought Threads formed from repeated, related activity sessions rather than screenshot volume

### Cloud only when explicitly requested
Gemini is used for:
- Normal JARVIS chat
- Explicit screen analysis
- Questions about an explicitly analyzed screen
- Memory/Thought Thread reasoning

Continuous recording does not send screenshots to Gemini.

## Privacy

- Screenshots are not stored by default.
- Recorded text, embeddings and metadata stay on the local machine.
- Runtime data is stored under `%LOCALAPPDATA%\SecondBrainAI`.
- Trusted-device credentials use Windows DPAPI when available.
- Settings provides memory export and deletion.
- Secrets and runtime databases are excluded from Git.

## Setup

1. Install Python 3.11 on Windows.
2. Create a virtual environment.
3. Install dependencies:

   `python -m pip install -r requirements.txt`

4. Optionally configure Gemini using `.env.example`.
5. Start with:

   `python app.py`

The application remains usable without a Gemini key. Local memory recording is off by default and requires explicit consent before the first recording session. Automatic recording is a separate opt-in in Settings and cannot be enabled without recording consent. The installer’s optional Windows sign-in launch task is unchecked by default; launching the app does not itself mean recording is enabled.

## Testing

Run:

`python -m pytest -q`

CI runs the test suite on Windows. The Windows build workflow also validates that the PyInstaller executable is produced.

## Windows release

Run:

`./build.ps1`

Then build the installer with Inno Setup using `installer.iss`.

## Release checklist

- Run tests on a clean Windows machine.
- Build and install the packaged application.
- Verify account creation, login, logout and trusted-device revocation.
- Verify recording with screenshots disabled.
- Verify screenshot retention when explicitly enabled.
- Verify memory export and deletion.
- Verify one long video/page session creates one memory with a start/end time range.
- Verify repeated visits to the same site become separate activity sessions and can form a related Thought Thread.
- Verify the app works without `GEMINI_API_KEY`.
- Verify explicit Gemini features with a valid key.
- Test idle/resume behavior.
- Verify first-run recording consent and that declining it leaves recording off.
- Verify recording remains off after login/restart unless both consent and auto-start are enabled.
- Verify revoking recording consent stops the active recorder immediately.
- Verify the installer does not add Windows startup unless the optional task is selected.
