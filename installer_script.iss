; Inno Setup Script for Gaan ta Namao

[Setup]
AppName=Gaan ta Namao
AppVersion=2.0
DefaultDirName={autopf}\Gaan ta Namao
DefaultGroupName=Gaan ta Namao
OutputBaseFilename=Gaan_ta_Namao_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\Gaan ta Namao.exe
AppPublisher=DS Mrinmoy

[Files]
; This tells the installer to grab your EXE from the dist folder
Source: "dist\Gaan ta Namao.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu Shortcut
Name: "{group}\Gaan ta Namao"; Filename: "{app}\Gaan ta Namao.exe"
; Desktop Shortcut
Name: "{autodesktop}\Gaan ta Namao"; Filename: "{app}\Gaan ta Namao.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"
