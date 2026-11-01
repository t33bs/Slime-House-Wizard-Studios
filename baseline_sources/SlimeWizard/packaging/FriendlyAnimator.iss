#ifndef AppVersion
  #define AppVersion "0.47.0"
#endif
[Setup]
AppId={{E59E68AC-73C7-40D5-9A3C-0E51FCED53CF}
AppName=Slime House Friendly Animator
AppVersion={#AppVersion}
DefaultDirName={autopf}\Slime House Friendly Animator
DefaultGroupName=Slime House Friendly Animator
OutputBaseFilename=SlimeHouseFriendlyAnimator-Setup-{#AppVersion}
OutputDir=..\dist-installer
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\SlimeHouseFriendlyAnimator.exe
SetupIconFile=..\studio\assets\wizard_slime.ico
CloseApplications=yes
RestartApplications=no

[Files]
Source: "..\dist\SlimeHouseFriendlyAnimator\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\Slime House Friendly Animator"; Filename: "{app}\SlimeHouseFriendlyAnimator.exe"
Name: "{autodesktop}\Slime House Friendly Animator"; Filename: "{app}\SlimeHouseFriendlyAnimator.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Run]
Filename: "{app}\SlimeHouseFriendlyAnimator.exe"; Description: "Launch Friendly Animator"; Flags: nowait postinstall skipifsilent
