[Setup]
AppName=RetailMan
AppVersion=2.0
DefaultDirName={pf}\RetailMan
DefaultGroupName=RetailMan
OutputDir=output
OutputBaseFilename=RetailMan_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "..\dist\RetailMan.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\RetailMan"; Filename: "{app}\RetailMan.exe"
Name: "{desktop}\RetailMan"; Filename: "{app}\RetailMan.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create Desktop Icon"; GroupDescription: "Additional Tasks"

[Run]
Filename: "{app}\RetailMan.exe"; Description: "Launch RetailMan"; Flags: nowait postinstall skipifsilent