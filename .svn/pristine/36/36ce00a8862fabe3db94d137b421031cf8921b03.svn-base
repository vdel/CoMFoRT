; CoMFoRT.nsi

; ---------------------------- Librairies -------------------------
; Style moderne
!include "MUI2.nsh"

; http://nsis.sourceforge.net/VersionCompare
;    $var=0  Versions are equal
;    $var=1  Version1 is newer
;    $var=2  Version2 is newer
!include "WordFunc.nsh"
!insertMacro VersionCompare

; Pour pages custom
!include nsDialogs.nsh

; Pour tests logiques
!include LogicLib.nsh

; ------------------- PARAMETRES GENERAUX ---------------------------

; Titre
Name "CoMFoRT"

; Fichier de sortie & Installeur Python (.msi)
!ifdef AMD64
  OutFile "Install-CoMFoRT-amd64.exe"
  !define PYTHON_INSTALLER "python-2.5.2.amd64.msi"
!else ifdef IA64
  OutFile "Install-CoMFoRT-ia64.exe"
  !define PYTHON_INSTALLER "python-2.5.2.ia64.msi"
!else 
  OutFile "Install-CoMFoRT-win32.exe"
  !define PYTHON_INSTALLER "python-2.5.2.msi"
!endif

; Repertoire d'installation par defaut
InstallDir $PROGRAMFILES\CoMFoRT
InstallDirRegKey HKLM "Software\CoMFoRT" "Install_Dir"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

; XP manifest
XPStyle on

; Installeur lxml (.exe)
!define LXML_INSTALLER "lxml-2.0.5.win32-py2.5.exe"

;---------------------- INSTALLATION -------------------------------

; Variables globales
Var StartMenuFolder
Var PythonVersion
Var PythonDir
Var PythonInstalled
Var JavaVersion
;Var JavaDir
Var JavaInstalled
Var Dialog
Var Label1
Var Label2
Var Label3
Var Label4
Var Label5
Var GroupBox1
Var GroupBox2
Var GroupBox3
Var verif_python_comment
Var verif_java
Var verif_lxml_comment

; Si abandon de l'installation
!define MUI_ABORTWARNING

; Images
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT
!define MUI_HEADERIMAGE_BITMAP logo.bmp
!define MUI_HEADERIMAGE_UNBITMAP logo.bmp

; Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT HKLM
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\CoMFoRT" 
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"

; Memorisation de la langue
  !define MUI_LANGDLL_REGISTRY_ROOT HKLM
  !define MUI_LANGDLL_REGISTRY_KEY "Software\CoMFoRT"
  !define MUI_LANGDLL_REGISTRY_VALUENAME "Installer Language"

; Parametres de la page finale
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT $(final_text)
!define MUI_FINISHPAGE_RUN_NOTCHECKED
!define MUI_FINISHPAGE_RUN_FUNCTION final_launch

; Pages d'installation
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE $(myLicenseData)
Page custom verif_func
!insertmacro MUI_PAGE_COMPONENTS
;!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!define MUI_PAGE_CUSTOMFUNCTION_PRE final_func
!insertmacro MUI_PAGE_FINISH

; Pages de desinstallation
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_COMPONENTS
!insertmacro MUI_UNPAGE_INSTFILES

; Fichiers de langue (premier par defaut)
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"

; Prechargement des langues
!insertmacro MUI_RESERVEFILE_LANGDLL

; Fichiers de license
LicenseLangString myLicenseData ${LANG_ENGLISH} "gpl-3.0.txt"
LicenseLangString myLicenseData ${LANG_FRENCH} "gpl-3.0.txt"

; Selection de la langue
Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

; Récupère la dernière version de Python installée
Function get_python_version
  StrCpy $0 0
  StrCpy $PythonVersion ""
  loop:
    ; les clés sont énumérées par ordre alpha
    EnumRegKey $1 HKLM Software\Python\PythonCore $0
    StrCmp $1 "" end
    IntOp $0 $0 + 1
    StrCpy $PythonVersion $1
    Goto loop
  end:
FunctionEnd

; Récupère le dossier de Python
Function get_python_dir
  ReadRegStr $PythonDir HKLM "Software\Python\PythonCore\$PythonVersion\InstallPath" ""
FunctionEnd

; Fonction pour determiner si python est installé
Function test_python_installed
  Call get_python_version
  StrCpy $PythonInstalled ""
  ${If} $PythonVersion == ""
    Goto end
  ${Else}
    Call get_python_dir
    ${If} $PythonDir == ""
      Goto end
    ${Else}
      IfFileExists "$PythonDir\python.exe" ok end
    ${EndIf}
  ${EndIf}
  ok:
    StrCpy $PythonInstalled "1"
  end:
FunctionEnd

; Récupère la dernière version du JRE installée
Function get_java_version
  StrCpy $0 0
  StrCpy $JavaVersion ""
  loop:
    ; les clés sont énumérées par ordre alpha
    EnumRegKey $1 HKLM "Software\JavaSoft\Java Runtime Environment" $0
    StrCmp $1 "" end
    IntOp $0 $0 + 1
    StrCpy $JavaVersion $1
    Goto loop
  end:
FunctionEnd

; Récupère le dossier de Java
;Function get_java_dir
;  ReadRegStr $JavaDir HKLM "Software\JavaSoft\Java Runtime Environment\$JavaVersion" "JavaHome"
;FunctionEnd

; Fonction pour determiner si java est installé
Function test_java_installed
  Call get_java_version
  StrCpy $JavaInstalled ""
  ${If} $JavaVersion == ""
    Goto end
  ${Else}
    IfFileExists "$SYSDIR\java.exe" ok end  ; Cherche dans C:\Windows\System32\ en général
  ${EndIf}
  ok:
    StrCpy $JavaInstalled "1"
  end:  
FunctionEnd

; Page de vérification
Function verif_func
  !insertmacro MUI_HEADER_TEXT $(verif_title) $(verif_subtitle)
  
  ; init
  SetOutPath $INSTDIR
  StrCpy $verif_lxml_comment $(verif_comment_lxml_no_test)
  
  Call test_python_installed
  ${If} $PythonInstalled == ""
    StrCpy $PythonVersion $(no_python)
    StrCpy $verif_python_comment $(verif_comment_no_python)
  ${Else} 
    ${VersionCompare} $PythonVersion "2.5" $0
    ${If} $0 == 2 
      StrCpy $verif_python_comment $(verif_comment_python_ko)
    ${Else}
      StrCpy $verif_python_comment $(verif_comment_python_ok)
      SectionSetFlags 1 0
      File "test_lxml.py"
      ExecWait '$PythonDir\python.exe "test_lxml.py"' $1
      ${If} $1 == 1
	StrCpy $verif_lxml_comment $(verif_comment_lxml_ok)
	SectionSetFlags 2 0
      ${ElseIf} $PythonVersion == "2.5"
        StrCpy $verif_lxml_comment $(verif_comment_lxml_ko)
      ${Else}
	StrCpy $verif_lxml_comment $(verif_comment_lxml_ko2)
	SectionSetFlags 2 0
      ${EndIf}
      Delete "test_lxml.py"
    ${EndIf}
  ${EndIf}
  
  Call test_java_installed
  ${If} $JavaInstalled == ""
    StrCpy $verif_java $(java_ko)
  ${Else}
    StrCpy $verif_java $(java_ok)
  ${EndIf}

  nsDialogs::Create /NOUNLOAD 1018
  Pop $Dialog
  ${If} $Dialog == error
    Abort
  ${EndIf}
  ${NSD_CreateGroupBox} 5% 0% 95% 50u " Python "
  Pop $GroupBox1
  ${NSD_CreateLabel} 10% 7% 80% 12u $(verif_python_version)
  Pop $Label1
  ${NSD_CreateLabel} 10% 17% 80% 20u $verif_python_comment
  Pop $Label2
  ${NSD_CreateGroupBox} 5% 36% 95% 48u " lxml "
  Pop $GroupBox2
  ${NSD_CreateLabel} 10% 42% 80% 35u $verif_lxml_comment
  Pop $Label3
  ${NSD_CreateGroupBox} 5% 71% 95% 40u $(pdf_generation)
  Pop $GroupBox3
  ${NSD_CreateLabel} 10% 77% 80% 12u $verif_java
  Pop $Label4
  ${NSD_CreateLabel} 10% 83% 80% 20u $(link_dblatex)
  Pop $Label5
  nsDialogs::Show
FunctionEnd



; Fonctions lancees à la fin
Function final_func
  Call test_python_installed ; si l'install vient de se faire
  ${If} $PythonInstalled == ""
    Abort
  ${EndIf}
  Call install_shortcuts
  ClearErrors
  FileOpen $0 "$INSTDIR\CoMFoRT_files\src\conf\confstatic.py" a
  IfErrors done
  FileSeek $0 0 END
  FileWrite $0 'nt_python_path="""$PythonDir """$\n'
  FileWrite $0 'nt_python_path=nt_python_path[:-1] #ugly$\n'
  ${If} $JavaVersion == ""
    FileWrite $0 "nt_has_java=False$\n"
  ${Else}
    FileWrite $0 "nt_has_java=True$\n"
  ${EndIf}
  FileClose $0
  done:
FunctionEnd

Function final_launch
  SetOutPath "$INSTDIR\CoMFoRT_files\src\server\"
  ExecShell "" "$PythonDir\python.exe" '"$INSTDIR\CoMFoRT_files\src\server\launch.py"'
FunctionEnd

; ------------------ Sections ------------------

Section $(Section1_name) Section1
  SectionIn RO
  
  ; On impose C:\CoMFoRT
  StrCpy $INSTDIR "C:\CoMFoRT"
  
  ; Repertoire de sortie
  SetOutPath $INSTDIR
  
  ; Fichiers à installer
  File /r CoMFoRT_files
  
  ; Ecriture du dossier d'installation dans le registre
  WriteRegStr HKLM SOFTWARE\CoMFoRT "Install_Dir" "$INSTDIR"
  
  ; Cles de desinstallation pour Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CoMFoRT" "DisplayName" "CoMFoRT"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CoMFoRT" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CoMFoRT" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CoMFoRT" "NoRepair" 1
  WriteUninstaller "uninstall.exe"
SectionEnd

Section $(Section2_name) Section2
  MessageBox MB_OK $(Python_Inst)
  SetOutPath $INSTDIR
  File "Python_files\${PYTHON_INSTALLER}"
  ExecWait 'msiexec /i "$INSTDIR\${PYTHON_INSTALLER}"'
  Delete "${PYTHON_INSTALLER}"
SectionEnd

Section $(Section3_name) Section3
  MessageBox MB_OK $(lxml_Inst)
  SetOutPath $INSTDIR
  File "lxml_files\${LXML_INSTALLER}"
  ExecWait '"${LXML_INSTALLER}"'
  Delete "${LXML_INSTALLER}"
SectionEnd

Function install_shortcuts
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\$(link_uninst).lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
    SetOutPath "$INSTDIR\CoMFoRT_files\src\server\"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\$(link_launch).lnk" "$PythonDir\python.exe" '"$INSTDIR\CoMFoRT_files\src\server\launch.py"' "$PythonDir\python.exe" 0
    ;CreateShortCut "$SMPROGRAMS\$StartMenuFolder\$(link_launch).lnk" ''"$INSTDIR\CoMFoRT_files\src\server\launch.py" "" "$INSTDIR\CoMFoRT_files\src\server\launch.py" 0
  !insertmacro MUI_STARTMENU_WRITE_END
FunctionEnd

; ----------------------- DESINSTALLATION -----------------------

Section un.$(uninst_comfort) UnSection1
  SectionIn RO
  
  ; Recupere le dossier des raccourcis
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
  ; Supprime les raccourcis
  Delete "$SMPROGRAMS\$StartMenuFolder\$(link_launch).lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\$(link_uninst).lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"

  ; Suppression des répertoires utilises
  RMDir /r "$INSTDIR"

  ; Supression des cles du registre
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CoMFoRT"
  DeleteRegKey HKLM SOFTWARE\CoMFoRT
SectionEnd

Section /o un.$(uninst_perso) UnSection2
  ; Suppression de .comfort dans le home
  RMDir /r "$PROFILE\.comfort"
SectionEnd

; Recuperation de la langue
Function un.onInit
  !insertmacro MUI_UNGETLANGUAGE
FunctionEnd


; ------------- Traduction --------------------

; Noms des sections
LangString Section1_name ${LANG_ENGLISH} "CoMFoRT (required)"
LangString Section1_name ${LANG_FRENCH} "CoMFoRT (requis)"
LangString Section2_name ${LANG_ENGLISH} "Python 2.5"
LangString Section2_name ${LANG_FRENCH} "Python 2.5"
LangString Section3_name ${LANG_ENGLISH} "lxml 2.0.5 for Python 2.5"
LangString Section3_name ${LANG_FRENCH} "lxml 2.0.5 pour Python 2.5"

; Descriptions des sections
LangString DESC_Section1 ${LANG_ENGLISH} "CoMFoRT main files."
LangString DESC_Section1 ${LANG_FRENCH} "Fichiers principaux de CoMFoRT."
LangString DESC_Section2 ${LANG_ENGLISH} "Run Python 2.5 Installer during CoMFoRT installation."
LangString DESC_Section2 ${LANG_FRENCH} "L'installation de Python 2.5 sera lancée durant l'installation de CoMFoRT."
LangString DESC_Section3 ${LANG_ENGLISH} "Run lxml 2.0.5 Installer during CoMFoRT installation."
LangString DESC_Section3 ${LANG_FRENCH} "L'installation de lxml 2.0.5 sera lancée durant l'installation de CoMFoRT."

; Page de verif
LangString verif_title ${LANG_ENGLISH} "Preliminary checks"
LangString verif_title ${LANG_FRENCH} "Vérifications préliminaires"
LangString verif_subtitle ${LANG_ENGLISH} "Python 2.5 and lxml are required by CoMFoRT."
LangString verif_subtitle ${LANG_FRENCH} "CoMFoRT nécessite Python 2.5 et lxml pour fonctionner."
LangString verif_python_version ${LANG_ENGLISH} "Python version detected : $PythonVersion"
LangString verif_python_version ${LANG_FRENCH} "Version de Python détectée : $PythonVersion"
LangString no_python ${LANG_ENGLISH} "not installed"
LangString no_python ${LANG_FRENCH} "non installé"
LangString verif_comment_no_python ${LANG_ENGLISH} "Python does not seem to be installed.$\nIt is recommended to select it on the next page."
LangString verif_comment_no_python ${LANG_FRENCH} "Python ne semble pas installé.$\nIl est recommandé de le sélectionner dans la suite de cette installation."
LangString verif_comment_python_ok ${LANG_ENGLISH} "A sufficiently recent version of Python is installed.$\nThere is no need to select it on the next page."
LangString verif_comment_python_ok ${LANG_FRENCH} "Une version suffisamment récente de Python est installée.$\nIl n'est pas nécessaire de le sélectionner dans la suite de cette installation."
LangString verif_comment_python_ko ${LANG_ENGLISH} "A too old version of Python is installed.$\nIt is recommended to select it on the next page."
LangString verif_comment_python_ko ${LANG_FRENCH} "Une version trop ancienne de Python est installée.$\nIl est recommandé de le sélectionner dans la suite de cette installation."
LangString verif_comment_lxml_no_test ${LANG_ENGLISH} "As Python is not installed or too old, the lxml detection has not been done.$\nIt is recommended to select it on the next page."
LangString verif_comment_lxml_no_test ${LANG_FRENCH} "Python n'étant pas installé ou trop ancien, la détection de lxml n'a pas été effectuée.$\nIl est recommandé de le sélectionner dans la suite de cette installation."
LangString verif_comment_lxml_ok ${LANG_ENGLISH} "lxml has correctly been detected.$\nThere is no need to select it on the next page."
LangString verif_comment_lxml_ok ${LANG_FRENCH} "lxml a été correctement détecté.$\nIl n'est pas nécessaire de le sélectionner dans la suite de cette installation."
LangString verif_comment_lxml_ko ${LANG_ENGLISH} "lxml is not installed on your computer.$\nAs you have Python 2.5, it is recommended to select it on the next page."
LangString verif_comment_lxml_ko ${LANG_FRENCH} "lxml n'est pas installé sur votre ordinateur.$\nComme vous disposez de Python 2.5, il est recommandé de le sélectionner dans la suite de cette installation."
LangString verif_comment_lxml_ko2 ${LANG_ENGLISH} "lxml is not installed on your computer.$\nAs your version of Python is not 2.5, the lxml version of the next page does not correspond to your configuration.$\nYou will have to install lxml yourself after the CoMFoRT installation."
LangString verif_comment_lxml_ko2 ${LANG_FRENCH} "lxml n'est pas installé sur votre ordinateur.$\nComme votre version de Python n'est pas 2.5, la version de lxml intégrée à cette installation ne convient pas.$\nVous devrez installer lxml par vous même après l'installation de CoMFoRT."
LangString pdf_generation ${LANG_ENGLISH} " PDF generation (Java required) "
LangString pdf_generation ${LANG_FRENCH} " Génération de PDF (Java requis) "
LangString link_dblatex ${LANG_ENGLISH} "For a better PDF quality, you can also install dblatex (http://dblatex.sourceforge.net)."
LangString link_dblatex ${LANG_FRENCH} "Pour une meilleure qualité des PDF, vous pouvez aussi installer dblatex (http://dblatex.sourceforge.net)."
LangString java_ok ${LANG_ENGLISH} "Java is already installed (version $JavaVersion)."
LangString java_ok ${LANG_FRENCH} "Java est déjà installé (version $JavaVersion)."
LangString java_ko ${LANG_ENGLISH} "You will have to install Java to activate PDF generation."
LangString java_ko ${LANG_FRENCH} "Vous devrez installer Java pour activer la génération PDF."

; Divers
LangString Python_Inst ${LANG_ENGLISH} "Python 2.5 will now be installed.$\n$\nWARNING: Due to a Python bug, the Python install path must not contain whitespaces! It is recommended to keep the default path."
LangString Python_Inst ${LANG_FRENCH} "Python 2.5 va maintenant être installé.$\n$\nATTENTION : Suite à un bug de Python, le chemin d'installation de Python ne doit pas contenir d'espace ! Il est recommandé de laisser le chemin par défaut."
LangString lxml_Inst ${LANG_ENGLISH} "lxml 2.0.5 will now be installed."
LangString lxml_Inst ${LANG_FRENCH} "lxml 2.0.5 va maintenant être installé."
LangString link_uninst ${LANG_ENGLISH} "Uninstall"
LangString link_uninst ${LANG_FRENCH} "Désinstaller" 
LangString link_launch ${LANG_ENGLISH} "Launch local server"
LangString link_launch ${LANG_FRENCH} "Lancer le serveur local"
LangString final_text ${LANG_ENGLISH} "Launch local server now."
LangString final_text ${LANG_FRENCH} "Lancer le serveur local maintenant."

; Désinstallation
LangString uninst_comfort ${LANG_ENGLISH} "Uninstall CoMFoRT (required)"
LangString uninst_comfort ${LANG_FRENCH} "Désinstaller CoMFoRT (requis)"
LangString uninst_perso ${LANG_ENGLISH} "Delete CoMFoRT configuration files and the created website"
LangString uninst_perso ${LANG_FRENCH} "Supprimer les fichiers de configuration et le site créé"

; Assignation des descriptions de section
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${Section1} $(DESC_Section1)
  !insertmacro MUI_DESCRIPTION_TEXT ${Section2} $(DESC_Section2)
  !insertmacro MUI_DESCRIPTION_TEXT ${Section3} $(DESC_Section3)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Assignation des descriptions de section
!insertmacro MUI_UNFUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${UnSection1} $(uninst_comfort)
  !insertmacro MUI_DESCRIPTION_TEXT ${UnSection2} $(uninst_perso)
!insertmacro MUI_UNFUNCTION_DESCRIPTION_END
