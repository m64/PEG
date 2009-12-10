!define PRODUCT_NAME "PARPG"
!define PRODUCT_VERSION "0.1"
!define PRODUCT_PUBLISHER "PARPG Development Team"
!define PRODUCT_WEB_SITE "http://blog.parpg.net/"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PARPG_DIR ".."
!define FIFE_DIR "../../.."

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${PARPG_DIR}\gui\icons\window_icon.ico"
!define MUI_UNICON "${PARPG_DIR}\gui\icons\window_icon.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

!insertmacro MUI_PAGE_COMPONENTS

; License page
!insertmacro MUI_PAGE_LICENSE "${PARPG_DIR}\LICENSE"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.rtf"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

RequestExecutionLevel admin ;For Vista. Admin is needed to install in program files directory

Name "${PRODUCT_NAME}"
OutFile "Setup.exe"
InstallDir "$PROGRAMFILES\PARPG"
ShowInstDetails show
ShowUnInstDetails show

;------------ Main. Packages PARPG code --------------
Section "PARPG" PARPG
  SetOutPath "$INSTDIR"
  SetOverwrite try
  
  ;Get all the core PARPG files
  FILE /r "${PARPG_DIR}\*ttf"
  FILE /r "${PARPG_DIR}\*.py"
  FILE /r "${PARPG_DIR}\*.yaml"
  FILE /r /x "settings.xml" "${PARPG_DIR}\*.xml"
  FILE /r "${PARPG_DIR}\*.png"
  FILE /r "${PARPG_DIR}\*.ico"
  FILE /r "${PARPG_DIR}\*.ogg"
  
  FILE "${PARPG_DIR}\README"
  FILE "${PARPG_DIR}\log_parpg.bat"

  RENAME "settings-dist.xml" "settings.xml"
  RENAME "README" "README.rtf"
  
  CreateDirectory "$INSTDIR\saves"
  
  ;Put all FIFE dependencies in a lib directory
  SetOutPath "$INSTDIR\lib\"
  FILE /r /x ".svn" "${FIFE_DIR}\engine\extensions"

  FILE "${FIFE_DIR}\engine\swigwrappers\python\fife.py"
  FILE "${FIFE_DIR}\engine\swigwrappers\python\_fife.pyd"
  FILE "${FIFE_DIR}\engine\swigwrappers\python\*dll"
  
  SetAutoClose true
SectionEnd

Section -AdditionalIcons
  ;avoid shortcuts headaches on vista by doing everything in the all users start menu
  SetShellVarContext all
  SetOutPath $INSTDIR
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateDirectory "$SMPROGRAMS\PARPG"
  CreateShortCut "$SMPROGRAMS\PARPG\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\PARPG\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  SetOutPath $INSTDIR ;this makes the following shortcut run in the installed directory
  CreateShortCut "$SMPROGRAMS\PARPG\PARPG.lnk" "$INSTDIR\run.py"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\gui\icons\window_icon.ico"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  ;avoid shortcuts headaches on vista by doing everything in the all users start menu
  SetShellVarContext all
  
  ;Remove all the code
  RMDir /r "$INSTDIR\dialogue"
  RMDir /r "$INSTDIR\editor"
  RMDir /r "$INSTDIR\fonts"
  RMDir /r "$INSTDIR\gui"
  RMDir /r "$INSTDIR\lib"
  RMDir /r "$INSTDIR\local_loaders"
  RMDir /r "$INSTDIR\maps"
  RMDir /r "$INSTDIR\music"
  RMDir /r "$INSTDIR\objects"
  RMDir /r "$INSTDIR\quests"
  RMDir /r "$INSTDIR\saves"
  RMDir /r "$INSTDIR\scripts"
  RMDir /r "$INSTDIR\tests"
  RMDir /r "$INSTDIR\utilities"
  
  Delete "$INSTDIR\dialogue_demo.py"
  Delete "$INSTDIR\dialogue_schema.yaml"
  Delete "$INSTDIR\PARPG"
  Delete "$INSTDIR\parpg_editor.py"
  Delete "$INSTDIR\run.py"
  Delete "$INSTDIR\run_tests.py"
  Delete "$INSTDIR\settings.py"
  Delete "$INSTDIR\settings.xml"
  Delete "$INSTDIR\README.rtf"
  Delete "$INSTDIR\log_parpg.bat"
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninstall.exe"
  
  RMDir "$INSTDIR"

  ;Remove shortcuts
  RMDir /r "$SMPROGRAMS\PARPG"
 
  ;Remove Registry keys
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  SetAutoClose true
SectionEnd

;---------- DOWNLOAD PYTHON -------
Section "ActivePython (required)" Python
  SetDetailsPrint textonly

  DetailPrint "Downloading Python"
  NSISdl::download http://downloads.activestate.com/ActivePython/windows/2.6/ActivePython-2.6.4.8-win32-x86.msi $TEMP/pysetup.msi
  Pop $R0 ;Get the return value
    StrCmp $R0 "success" +3
      MessageBox MB_OK "Failed to download Python installer: $R0"
      Quit

  DetailPrint "Installing Python"
  ExecWait '"msiexec" /i "$TEMP\pysetup.msi"'

  DetailPrint "Deleting Python installer"
  Delete $TEMP\pysetup.msi
SectionEnd

;------------ PyYAML --------------
Section "PyYAML (required)" PyYAML
  SetDetailsPrint textonly

  SetOutPath "$SYSDIR"        ;Some Systems need this DLL to install PyYAML properly
  ;SetOverwrite ifnewer
  ;File "requs\msvcr71.dll"
  ;SetOverwrite on
  
  NSISdl::download http://pyyaml.org/download/pyyaml/PyYAML-3.09.win32-py2.6.exe $TEMP\pyaml_setup.exe
  Pop $R0 ;Get the return value
    StrCmp $R0 "success" +3
      MessageBox MB_OK "Failed to download PyYAML installer: $R0"
      Quit

  
  SetOutPath "$TEMP"
  DetailPrint "Installing PyYAML"
  ExecWait "$TEMP\pyaml_setup.exe"

  DetailPrint "Deleting PyYAML installer"
  Delete "$TEMP\PyYAML_setup.exe"
SectionEnd
;----------- OPEN AL --------------
Section "OpenAL (required)" OpenAL
  SetDetailsPrint textonly

  ;oalinst.exe must be downloaded seperately and put into the
  ;dependencies directory for packaging to be successful
  SetOutPath "$TEMP"
  File ".\dependencies\oalinst.exe"
  DetailPrint "Installing OpenAL"
  ExecWait "$TEMP\oalinst.exe"

  DetailPrint "Deleting OpenAL installer"
  Delete "$TEMP\oalinst.exe"
SectionEnd
;--------- SECTION END ------------

LangString DESC_PARPG ${LANG_ENGLISH} "PARPG - The game code"
LangString DESC_Python ${LANG_ENGLISH} "ActivePython 2.6.4.8 - Required to run PARPG. Requires an active internet connection to install."
LangString DESC_PyYAML ${LANG_ENGLISH} "PyYAML 3.09 - Required Python Module. Requires an active internet connection to install."
LangString DESC_OpenAL ${LANG_ENGLISH} "OpenAL - Required for sound and music"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${PARPG} $(DESC_PARPG)
  !insertmacro MUI_DESCRIPTION_TEXT ${Python} $(DESC_Python)
  !insertmacro MUI_DESCRIPTION_TEXT ${PyYAML} $(DESC_PyYAML)
  !insertmacro MUI_DESCRIPTION_TEXT ${OpenAL} $(DESC_OpenAL)
!insertmacro MUI_FUNCTION_DESCRIPTION_END