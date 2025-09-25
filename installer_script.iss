; Inno Setup Script for "Gaan ta Namao"

[Setup]
AppName=Gaan ta Namao
AppVersion=1.0
DefaultDirName={autopf}\Gaan ta Namao
DefaultGroupName=Gaan ta Namao
UninstallDisplayIcon={app}\Gaan ta Namao.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
OutputBaseFilename=Gaan_ta_Namao_Setup
SetupIconFile=logo.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; This tells the installer to take your exe from the 'dist' folder
; and place it in the installation directory.
Source: "dist\Gaan ta Namao.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Create a shortcut in the Start Menu's program group
Name: "{group}\Gaan ta Namao"; Filename: "{app}\Gaan ta Namao.exe"

; Create a shortcut on the user's Desktop
Name: "{autodesktop}\Gaan ta Namao"; Filename: "{app}\Gaan ta Namao.exe"; Tasks: desktopicon

[Tasks]
; This gives the user an option to create a desktop icon during installation
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";

[Run]
; This gives the user an option to launch the application right after installation finishes
Filename: "{app}\Gaan ta Namao.exe"; Description: "{cm:LaunchProgram,Gaan ta Namao}"; Flags: nowait postinstall skipifsilent;
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
