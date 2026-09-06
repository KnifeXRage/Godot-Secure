#!/bin/bash

# @author: Twister
# @contact: https://github.com/CodeNameTwister
# @license: Twister Wasting Time Copyrights by a company that wastes time, all time is reserved.


# Godot Secure Version
clear
VER='4.0'

echo "Godot Secure Version $VER Github: 'https://github.com/KnifeXRage/Godot-Secure'"

echo '[94m'
echo '::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::'
echo ' _____           _       _     _____                          '
echo '|  __ \         | |     | |   /  ___|                         '
echo '| |  \/ ___   __| | ___ | |_  \ `--.  ___  ___ _   _ _ __ ___ '
echo '| | __ / _ \ / _` |/ _ \| __|  `--. \/ _ \/ __| | | | '__/ ___'\'
echo '| |_\ \ (_) | (_| | (_) | |_  /\__/ /  __/ (__| |_| | | |  __/'
echo ' \____/\___/ \__,_|\___/ \__| \____/ \___|\___|\__,_|_|  \___|'
echo '::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::'
echo '[0m'

# init 1
# ========================================================

# =======================
#      CHECK P11T0N
# =======================
__PY__='python'
__OMSG__='Press any key to continue...'

if !command -v $__PY__ &> /dev/null; then
    if !command -v py &> /dev/null; then
        echo "Python no está instalado."
        # init 0
        echo '[[91mCRITICAL[0m] Python is not installed or can not find in the environment PATH.'
        echo 'You can download python on "https://www.python.org" and make sure add python to environment PATH.'
        read -p "$__OMSG__"
        exit /b 1
    fi
    __PY__='py'
fi

command $__PY__ -c "import sys; exit(0) if sys.version_info >= (3, 10) else exit(1)" >nul 2>&1

if [ $? -ne 0 ]; then
    # init 0
    echo '[[91mERROR[0m] Python version >= 3.10 is required!, you can download in: "https://www.python.org"'
    echo 'You current version:'
    command $__PY__ --version
    read -p "$__OMSG__"
    exit $?
fi

echo '[[92mOK[0m] Python is installed.'

# X1 MM
# ========================================================

_ST=0
__DIR__="$(dirname "$0")"

init(){
    _OP[0]=4
    _OP[1]='Set Encryption Key'
    _OP[2]='Run Godot Secure Script'
    _OP[3]='Restore Backup Files'
    _OP[4]='[93mExit[0m'

    _FNC[0]='init'
    _FNC[1]='set_key'
    _FNC[2]='menu_ver'
    _FNC[3]='menu_restore'
    _FNC[4]='_exit'

    if [ $_ST -gt 0 ]; then
        clear
    fi

    _ST=1

    echo '[94m'
    echo '===================================='
    echo '        Godot-Secure Options'
    echo '===================================='

    echo;

    
    _op_
}

_op_(){
    next='_back'
    echo '[93mMenu[92m'

    for i in $(seq 1 ${_OP[0]}); do
        echo "$i. ${_OP[$i]}"
    done
    echo;
    read -p "Select an option :(1-${_OP[0]}): " op

    if ! [[ $op =~ ^[0-9]+$ ]]; then
        op=-1
    fi

    if [ $op -gt 0 ]; then
        if [ $op -le ${_OP[0]} ]; then
            next=${_FNC[$op]}
        fi
    fi
    $next
}

_back(){
    echo 'Invalid selection, try again.'
    read -p "$__OMSG__"
    ${_FNC[0]}
}

:: X2 SM
:: ========================================================
set_key(){
    clear
    echo '[94m'
    echo '===================================='
    echo '          Encryption Key'
    echo '===================================='
    echo '[0mSet you generated 256-bit key[92m'
    echo;

    read -p "Encryption key:" op
    export SCRIPT_AES256_ENCRYPTION_KEY=$op

    init
}

menu_ver(){
    clear
    echo '[94m'
    echo '===================================='
    echo '          GODOT VERSION'
    echo '===================================='
    echo '[0mWhat is you Godot Version?[92m'
    echo;

    _OP[0]=3
    _OP[1]='Godot 4.6 or greater'
    _OP[2]='Godot 4.5 or minor'
    _OP[3]='[93mBack[0m'
    
    _FNC[0]='menu_ver'
    _FNC[1]='menu_4_6'
    _FNC[2]='menu_4_5'
    _FNC[${_OP[0]}]='init'

    _op_
}

menu_4_6(){
    fscript='v4.6.x - Latest'
    fback='menu_4_6'
    list
}

menu_4_5(){
    fscript='v4.x.x - v4.5.x'
    fback='menu_4_5'
    list
}

list(){
    clear
    echo '[94m'
    echo '===================================='
    echo '           SELECT SCRIPT'
    echo '===================================='
    xfiles=0

    for f in "$__DIR__/$fscript"/*.py; do
        [ -e "$f" ] || continue
        ((xfiles++))
        _OP[$xfiles]=$(basename "$f")
    done

    ((xfiles++))
    _OP[0]=$xfiles
    _OP[$xfiles]="[93mBack[0m"


    for (( i=1; i<=$xfiles; i++ )); do
        _FNC[$i]="run_script"
    done

    _FNC[0]=$fback
    _FNC[$xfiles]='menu_ver'

    _op_
}

run_script(){
    clear
    echo "[92mScript selected ${_OP[$op]}[0m"

    echo;
    echo 'Please set the "godot" directory'
    echo '(Example: "C:/my_folder/godot")'
    echo;
    read -p "Godot directory:" gd
    echo "Trying use godot directory: $gd"
    echo Starting run Godot Secure Script...
    echo;
    command $__PY__ "$__DIR__/$fscript/${_OP[$op]}" $gd
    echo;
    echo 'Operation ended, back to main menu.'
    read -p "$__OMSG__"
    init
}

menu_restore(){
    clear
    echo '[94m'
    echo '===================================='
    echo '       RESTORE BACKUP'
    echo '===================================='
    echo '[0mAre you sure restore backup?[92m'
    echo;
    _OP[0]=2
    _OP[1]='Yes'
    _OP[2]='[93mNo[0m'

    _FNC[0]='menu_restore'
    _FNC[1]='restore_backup'
    _FNC[2]='init'

    _op_
}

restore_backup(){
    clear
    echo '[92mStarting Restore Backup...[0m'
    echo;
    echo 'Please set the "godot" directory'
    echo '(Example: "C:/my_folder/godot")'
    echo;

    read -p "Godot directory:" gd
    echo "Trying use godot directory: $gd"

    command $__PY__ "$__DIR__/utils/restore_backup.py" $gd
    echo;
    echo 'Operation ended, back to main menu.'
    read -p "$__OMSG__"

    init
}

_exit(){
    #X0 SIGTERM
    echo Exiting...
    exit 0
}

init