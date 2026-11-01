#define AppName "Slime House Wizard Studios"
#define AppVersion "0.1.4"
#define AppExe "SlimeHouseWizardStudios.exe"
[Setup]
AppId={{C4C7A50B-1984-4A39-86B4-E1097BD0B52A}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Slime House Studios
DefaultDirName={localappdata}\Programs\Slime House Wizard Studios
DefaultGroupName={#AppName}
OutputDir=..\installer-output
OutputBaseFilename=SlimeHouseWizardStudios-Build14-Setup
Compression=lzma2
SolidCompression=yes
SetupIconFile=..\assets\slime_house_studios.ico
UninstallDisplayIcon={app}\{#AppExe}
PrivilegesRequired=lowest
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
Uninstallable=yes

[Files]
Source: "..\dist\SlimeHouseWizardStudios\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
