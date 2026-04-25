[Setup]
AppId=RetailManApp
AppName=RetailMan
AppVersion=2.0
DefaultDirName={localappdata}\RetailMan
DefaultGroupName=RetailMan
OutputDir=output
OutputBaseFilename=RetailMan_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=..\public\retailman_logo.ico
PrivilegesRequired=lowest

[Files]
Source: "..\dist\RetailMan.exe"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Create Desktop Icon"; GroupDescription: "Additional Tasks"; Flags: unchecked

[Icons]
Name: "{group}\RetailMan"; Filename: "{app}\RetailMan.exe"
Name: "{userdesktop}\RetailMan"; Filename: "{app}\RetailMan.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\RetailMan.exe"; Description: "Launch RetailMan"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\*.*"
Type: dirifempty; Name: "{app}"

[Messages]
WelcomeLabel2=This will install RetailMan on your computer.%n%nClick Next to continue.

[Code]
procedure CreateEnvFile();
var
  FilePath: string;
  DirPath: string;
begin
  DirPath := ExpandConstant('{localappdata}\RetailMan');

  if not DirExists(DirPath) then
    CreateDir(DirPath);

  FilePath := DirPath + '\.env';

  if not FileExists(FilePath) then
  begin
    SaveStringToFile(FilePath,
      'DB_HOST=localhost'#13#10 +
      'DB_USER=root'#13#10 +
      'DB_PORT=3306'#13#10 +
      'DB_PASSWORD=Password@123'#13#10 +
      'DB_NAME=retail_man_db',
      False
    );
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    CreateEnvFile();
  end;
end;