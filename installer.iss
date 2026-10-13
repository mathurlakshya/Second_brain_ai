#define MyAppName "Second Brain AI"
#define MyAppVersion "1.0.0"
#define MyAppExeName "SecondBrainAI.exe"

[Setup]
AppId={{B4C7B1B2-9F31-4E7B-9C1D-SECOND-BRAIN-AI}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}Second Brain AI
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=SecondBrainAI-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin

[Files]
Source: "dist\SecondBrainAI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "startup"; Description: "Launch Second Brain AI when I sign in (recording requires a separate opt-in in Settings)"; GroupDescription: "Optional settings:"; Flags: unchecked

[Registry]
; Startup is an explicit installer opt-in. Recording remains separately disabled by default.
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "SecondBrainAI"; ValueData: """"{app}\{#MyAppExeName}""""; Flags: uninsdeletevalue; Tasks: startup

[Icons]
Name: "{group}\Second Brain AI"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\Second Brain AI"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Second Brain AI"; Flags: nowait postinstall skipifsilent
