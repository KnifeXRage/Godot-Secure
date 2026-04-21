@echo off
setlocal enabledelayedexpansion
:: @author: Twister
:: @contact: https://github.com/CodeNameTwister
:: @license: Twister Wasting Time Copyrights by a company that wastes time, all time is reserved.


:: Godot Secure Version
cls
SET VER=4.0

echo Godot Secure Version %VER% Github: https://github.com/KnifeXRage/Godot-Secure

echo [94m
echo "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
echo " _____           _       _     _____                          "
echo "|  __ \         | |     | |   /  ___|                         "
echo "| |  \/ ___   __| | ___ | |_  \ `--.  ___  ___ _   _ _ __ ___ "
echo "| | __ / _ \ / _` |/ _ \| __|  `--. \/ _ \/ __| | | | '__/ _ \"
echo "| |_\ \ (_) | (_| | (_) | |_  /\__/ /  __/ (__| |_| | | |  __/"
echo " \____/\___/ \__,_|\___/ \__| \____/ \___|\___|\__,_|_|  \___|"
echo "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
echo [0m

:: init 1
:: ========================================================

:: =======================
::      CHECK P11T0N
:: =======================
SET __PY__=python

where %__PY__% >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% neq 0 (
        :: init 0
        echo [[91mCRITICAL[0m] Python is not installed or can not find in the environment PATH.      
        echo You can download python on "https://www.python.org" and make sure add python to environment PATH.
        pause
        exit /b 1
    )

    SET __PY__=py
)

%__PY__% -c "import sys; exit(0) if sys.version_info >= (3, 10) else exit(1)" >nul 2>&1

if %errorlevel% neq 0 (
    :: init 0
    echo [[91mERROR[0m] Python version >= 3.10 is required!, you can download in: "https://www.python.org"
    echo You current version:
    %__PY__% --version
    pause
    exit /b %errorlevel%
)

echo [[92mOK[0m] Python is installed.

:: X1 MM
:: ========================================================

SET _ST=0
SET __DIR__=%~dp0

:INIT

SET _OP[0]=4
SET "_OP[1]=Set Encryption Key"
SET "_OP[2]=Run Godot Secure Script"
SET "_OP[3]=Restore Backup Files"
SET "_OP[4]=[93mExit[0m"

SET _FNC[0]=INIT
SET _FNC[1]=SET_KEY
SET _FNC[2]=MENU_VER
SET _FNC[3]=MENU_RESTORE
SET _FNC[4]=EXIT

if %_ST% GTR 0 (
   CLS
)

SET _ST=1

echo [94m
echo ====================================
echo        Godot-Secure Options
echo ====================================

:_OP_
echo [93mMenu[92m

for /L %%i in (1,1,%_OP[0]%) do (
    echo %%i. !_OP[%%i]!
)

echo.

SET /p op="Select an option (1-%_OP[0]%): "


if %op% GTR 0 (
    if %op% LEQ %_OP[0]% (
        goto !_FNC[%op%]!
    )
)

echo Invalid selection, try again.
pause
goto !_FNC[0]!

:: X2 SM
:: ========================================================
:SET_KEY
    CLS
    echo [94m
    echo ====================================
    echo           Encryption Key
    echo ====================================
    echo [0mSet you generated 256-bit key[92m
    echo/

    SET /p op="Encryption Key:"
    SET SCRIPT_AES256_ENCRYPTION_KEY=$op

    goto INIT

:MENU_VER
CLS
echo [94m
echo ====================================
echo           GODOT VERSION
echo ====================================
echo [0mWhat is you Godot Version?[92m
echo.

SET _OP[0]=3
SET "_OP[1]=Godot 4.6 or greater"
SET "_OP[2]=Godot 4.5 or minor"
SET "_OP[3]=[93mBack[0m"

SET _FNC[0]=MENU_VER
SET _FNC[1]=MENU_4_6
SET _FNC[2]=MENU_4_5
SET _FNC[%_OP[0]%]=INIT

goto _OP_

:MENU_4_6
SET fscript=v4.6.x - Latest
SET fback=MENU_4_6
goto LIST

:MENU_4_5
SET fscript=v4.x.x - v4.5.x
SET fback=MENU_4_5
goto LIST

:LIST
CLS
echo [94m
echo ====================================
echo            SELECT SCRIPT
echo ====================================
SET /a xfiles=0
for /f "delims=" %%f in ('dir /b /a-d "%__DIR__%%fscript%\*.py" 2^>nul') do ( 
    SET /a xfiles+=1
    SET _OP[!xfiles!]=%%f
)
SET /a xfiles+=1
SET "_OP[0]=%xfiles%"
SET "_OP[%xfiles%]=[93mBack[0m"

for /L %%i in (1,1,%xfiles%) do (
    SET "_FNC[%%i]=RUN_SCRIPT"
)

SET _FNC[0]=%fback%
SET _FNC[%xfiles%"]=MENU_VER

goto _OP_

:RUN_SCRIPT
CLS
echo [92mScript selected !_OP[%op%]![0m

echo.
echo Please set the "godot" directory
echo (Example: "C:/my_folder/godot")
echo.
SET /p gd="Godot directory: "
echo Trying use the godot directory: %gd%
echo Starting run Godot Secure Script...
echo.
%__PY__% "%__DIR__%%fscript%\!_OP[%op%]!" %gd%
echo.
echo Operation ended, back to main menu.
pause
GOTO INIT

:MENU_RESTORE
CLS
echo [94m
echo ====================================
echo        RESTORE BACKUP
echo ====================================
echo [0mAre you sure restore backup?[92m
echo.
SET _OP[0]=2
SET "_OP[1]=Yes"
SET "_OP[2]=[93mNo[0m"

SET _FNC[0]=MENU_RESTORE
SET _FNC[1]=RESTORE_BACKUP
SET _FNC[2]=INIT

goto _OP_

:RESTORE_BACKUP
CLS
echo [92mStarting Restore Backup...[0m
echo.
echo Please set the "godot" directory
echo (Example: "C:/my_folder/godot")
echo.

SET /p gd="Godot directory: "
echo Trying use the godot directory: %gd%
%__PY__% "%__DIR___%utils/restore_backup.py" %gd%
echo.
echo Operation ended, back to main menu.
pause

goto INIT

goto EXIT

:: X0 SIGTERM
:: ========================================================
:EXIT
echo Exiting...
timeout /t 2 >nul
exit