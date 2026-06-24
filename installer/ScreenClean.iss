; Screen Clean — styled Windows installer (Inno Setup 6+)

#define AppVersion "3.2.0"
#define AppName "Screen Clean"
#define AppPublisher "printHESOYAM"
#define AppURL "https://github.com/printHESOYAM/screen-clean"
#define ExeName "ScreenClean.exe"

[Setup]
AppId={{8F4E2A1B-9C3D-4E5F-A712-3B6C9D0E1F2A}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=ScreenClean-Setup
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#ExeName}
WizardStyle=modern
WizardSizePercent=115
WizardImageFile=assets\wizard-large.bmp
WizardSmallImageFile=assets\wizard-small.bmp
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
ShowLanguageDialog=auto
LicenseFile=
InfoBeforeFile=
ChangesAssociations=no
DisableWelcomePage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[CustomMessages]
english.WelcomeLabel2=This will install [name/ver] on your computer.%n%nScreen Clean automatically sorts files on your desktop into an archive folder.%n%nIt runs quietly in the system tray.
russian.WelcomeLabel2=Будет установлен [name/ver] на ваш компьютер.%n%nScreen Clean автоматически сортирует файлы на рабочем столе в папку-архив.%n%nПриложение работает в системном трее.
english.FinishedLabel=Screen Clean has been installed.%n%nLaunch it from the Start menu or the tray icon.
russian.FinishedLabel=Screen Clean установлен.%n%nЗапустите из меню «Пуск» или через иконку в трее.

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon,{#AppName}}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\{#ExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#ExeName}"; Comment: "Automatic desktop sorting"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#ExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#ExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
