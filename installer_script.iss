[Setup]
AppName=ORMTexturePacker
AppVersion=1.0
DefaultDirName={pf}\ORMTexturePacker
OutputDir=Output
OutputBaseFilename=ORMTexturePackerInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\ORMTexturePacker.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ORMTexturePacker"; Filename: "{app}\main.exe"
