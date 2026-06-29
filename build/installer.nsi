; DolphinPhoto AI Studio - NSIS Installer Script
; Creates a Windows .exe installer

!include "MUI2.nsh"
!include "FileFunc.nsh"

; General
Name "DolphinPhoto AI Studio"
OutFile "DolphinPhoto-Setup.exe"
InstallDir "$PROGRAMFILES\DolphinPhoto AI Studio"
InstallDirRegKey HKLM "Software\DolphinPhoto" "InstallDir"
RequestExecutionLevel admin

; Version Info
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "DolphinPhoto AI Studio"
VIAddVersionKey "CompanyName" "Black Tiger Computing"
VIAddVersionKey "LegalCopyright" "Copyright (c) 2024 Black Tiger Computing"
VIAddVersionKey "FileDescription" "DolphinPhoto AI Studio Installer"
VIAddVersionKey "FileVersion" "1.0.0"
VIAddVersionKey "ProductVersion" "1.0.0"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installation Section
Section "DolphinPhoto AI Studio" SecMain
    SetOutPath "$INSTDIR"
    
    ; Copy all files from dist
    File /r "..\dist\*.*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Create Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\DolphinPhoto AI Studio"
    CreateShortcut "$SMPROGRAMS\DolphinPhoto AI Studio\DolphinPhoto.lnk" "$INSTDIR\DolphinPhoto.bat"
    CreateShortcut "$SMPROGRAMS\DolphinPhoto AI Studio\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    
    ; Create Desktop shortcut
    CreateShortcut "$DESKTOP\DolphinPhoto AI Studio.lnk" "$INSTDIR\DolphinPhoto.bat"
    
    ; Write registry keys for uninstall
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DolphinPhoto" "DisplayName" "DolphinPhoto AI Studio"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DolphinPhoto" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DolphinPhoto" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DolphinPhoto" "Publisher" "Black Tiger Computing"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DolphinPhoto" "DisplayVersion" "1.0.0"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DolphinPhoto" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DolphinPhoto" "NoRepair" 1
    
    ; Get and write installed size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DolphinPhoto" "EstimatedSize" "$0"
    
    ; Store install dir
    WriteRegStr HKLM "Software\DolphinPhoto" "InstallDir" "$INSTDIR"
SectionEnd

; Uninstall Section
Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove Start Menu shortcuts
    RMDir /r "$SMPROGRAMS\DolphinPhoto AI Studio"
    
    ; Remove Desktop shortcut
    Delete "$DESKTOP\DolphinPhoto AI Studio.lnk"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DolphinPhoto"
    DeleteRegKey HKLM "Software\DolphinPhoto"
SectionEnd

; Section Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Install DolphinPhoto AI Studio - The Ultimate AI Creative Studio"
!insertmacro MUI_FUNCTION_DESCRIPTION_END
