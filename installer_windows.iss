; Script do Inno Setup para gerar um instalador .exe do Conversor de Documentos.
;
; Como usar (no Windows):
;   1. Rode "instalar_e_rodar.bat" (ou o comando pyinstaller do README) para gerar
;      "dist\ConversorDeDocumentos.exe" primeiro.
;   2. Instale o Inno Setup (gratuito): https://jrsoftware.org/isinfo.php
;   3. Abra este arquivo com o Inno Setup Compiler e clique em "Compile"
;      (ou rode via linha de comando: ISCC.exe installer_windows.iss).
;   4. O instalador final fica em "installer_output\ConversorDeDocumentos_Setup.exe".

#define MyAppName "Conversor de Documentos"
#define MyAppVersion "2.0"
#define MyAppExeName "ConversorDeDocumentos.exe"

[Setup]
AppId={{8F3C7E2A-6B1D-4E9A-9C3F-1A2B3C4D5E6F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\ConversorDeDocumentos
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=installer_output
OutputBaseFilename=ConversorDeDocumentos_Setup
SetupIconFile=assets\icon.ico
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
PrivilegesRequired=lowest

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar um atalho na Área de Trabalho"; GroupDescription: "Atalhos:"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir o Conversor de Documentos"; Flags: nowait postinstall skipifsilent
