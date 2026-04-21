# :: @author: Twister
# :: @contact: https://github.com/CodeNameTwister
# :: @license: Twister Wasting Time Copyrights by a company that wastes time, all time is reserved.

# :: Godot Secure Version
Clear-Host
$VER = "4.0"

Write-Host "Godot Secure Version $VER Github: https://github.com/KnifeXRage/Godot-Secure"

Write-Host -ForegroundColor Cyan "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
Write-Host -ForegroundColor Cyan " _____           _       _     _____                          "
Write-Host -ForegroundColor Cyan "|  __ \         | |     | |   /  ___|                         "
Write-Host -ForegroundColor Cyan "| |  \/ ___   __| | ___ | |_  \ \`--.  ___  ___ _   _ _ __ ___"
Write-Host -ForegroundColor Cyan "| | __ / _ \ / _\` |/ _ \| __|  \`--. \/ _ \/ __| | | | '__/ _ \"
Write-Host -ForegroundColor Cyan "| |_\ \ (_) | (_| | (_) | |_  /\__/ /  __/ (__| |_| | | |  __/"
Write-Host -ForegroundColor Cyan " \____/\___/ \__,_|\___/ \__| \____/ \___|\___|\__,_|_|  \___|"
Write-Host -ForegroundColor Cyan "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"

# :: init 1
# :: =======================
# ::      CHECK P11T0N
# :: =======================
$__PY__ = "python"

if (-not (Get-Command $__PY__ -ErrorAction SilentlyContinue)) {
    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        # :: init 0
        Write-Host "[ " -NoNewline; Write-Host -ForegroundColor Red "CRITICAL" -NoNewline; Write-Host " ] Python is not installed or can not find in the environment PATH."
        Write-Host "You can download python on `"https://www.python.org`" and make sure add python to environment PATH."
        Pause
        exit 1
    }
    $__PY__ = "py"
}

& $__PY__ -c "import sys; exit(0) if sys.version_info >= (3, 10) else exit(1)"
if ($LASTEXITCODE -ne 0) {
    # :: init 0
    Write-Host "[ " -NoNewline; Write-Host -ForegroundColor Red "ERROR" -NoNewline; Write-Host " ] Python version >= 3.10 is required!, you can download in: `"https://www.python.org`""
    Write-Host "You current version:"
    & $__PY__ --version
    Pause
    exit $LASTEXITCODE
}

Write-Host "[ " -NoNewline; Write-Host -ForegroundColor Green "OK"  -NoNewline; Write-Host " ] Python is installed."
# :: X1 MM
# :: ========================================================

$_ST = 0
$__DIR__ = $PSScriptRoot

function INIT {
    $global:_OP = @{}
    $global:_OP[0] = 4
    $global:_OP[1] = "Set Encryption Key"
    $global:_OP[2] = "Run Godot Secure Script"
    $global:_OP[3] = "Restore Backup Files"
    $global:_OP[4] = "Exit"

    $global:_FNC = @{}
    $global:_FNC[0] = "INIT"
    $global:_FNC[1] = "SET_KEY"
    $global:_FNC[2] = "MENU_VER"
    $global:_FNC[3] = "MENU_RESTORE"
    $global:_FNC[4] = "EXIT_FUNC"

    if ($_ST -gt 0) {
        Clear-Host
    }

    $_ST = 1

    Write-Host -ForegroundColor Cyan "===================================="
    Write-Host -ForegroundColor Cyan "        Godot-Secure Options"
    Write-Host -ForegroundColor Cyan "===================================="

    _OP_
}

function _OP_ {
    Write-Host -ForegroundColor Yellow "Menu " -NoNewline; Write-Host -ForegroundColor Green ""
    
    for ($i = 1; $i -le $_OP[0]; $i++) {
        if ($i -eq $_OP[0]) {
            Write-Host "$i. " -NoNewline; Write-Host -ForegroundColor Yellow "$($_OP[$i])"
        } else {
            Write-Host "$i. $($_OP[$i])"
        }
    }

    Write-Host ""
    $op = Read-Host "Select an option (1-$($_OP[0]))"

    if ($op -gt 0 -and $op -le $_OP[0]) {
        $target = $_FNC[[int]$op]
        & $target
    } else {
        Write-Host "Invalid selection, try again."
        Pause
        & $_FNC[0]
    }
}

# :: X2 SM
# :: ========================================================
function SET_KEY {
    Clear-Host
    Write-Host -ForegroundColor Cyan "===================================="
    Write-Host -ForegroundColor Cyan "           Encryption Key"
    Write-Host -ForegroundColor Cyan "===================================="
    Write-Host "Set you generated 256-bit key " -NoNewline; Write-Host -ForegroundColor Green ""
    Write-Host ""

    $op = Read-Host "Encryption Key"
    $env:SCRIPT_AES256_ENCRYPTION_KEY = $op

    INIT
}

function MENU_VER {
    Clear-Host
    Write-Host -ForegroundColor Cyan "===================================="
    Write-Host -ForegroundColor Cyan "           GODOT VERSION"
    Write-Host -ForegroundColor Cyan "===================================="
    Write-Host "What is you Godot Version?"
    Write-Host ""

    $global:_OP = @{}
    $global:_OP[0] = 3
    $global:_OP[1] = "Godot 4.6 or greater"
    $global:_OP[2] = "Godot 4.5 or minor"
    $global:_OP[3] = "Back"

    $global:_FNC = @{}
    $global:_FNC[0] = "MENU_VER"
    $global:_FNC[1] = "MENU_4_6"
    $global:_FNC[2] = "MENU_4_5"
    $global:_FNC[3] = "INIT"

    _OP_
}

function MENU_4_6 {
    $global:fscript = "v4.6.x - Latest"
    $global:fback = "MENU_4_6"
    LIST
}

function MENU_4_5 {
    $global:fscript = "v4.x.x - v4.5.x"
    $global:fback = "MENU_4_5"
    LIST
}

function LIST {
    Clear-Host
    Write-Host -ForegroundColor Cyan "===================================="
    Write-Host -ForegroundColor Cyan "            SELECT SCRIPT"
    Write-Host -ForegroundColor Cyan "===================================="
    
    $global:xfiles = 0
    $global:_OP = @{}
    $global:_FNC = @{}
    
    $files = Get-ChildItem -Path "$__DIR__\$fscript\*.py" -ErrorAction SilentlyContinue
    foreach ($f in $files) {
        $global:xfiles++
        $global:_OP[$xfiles] = $f.Name
        $global:_FNC[$xfiles] = "RUN_SCRIPT"
    }
    
    $global:xfiles++
    $global:_OP[0] = $xfiles
    $global:_OP[$xfiles] = "Back"
    $global:_FNC[0] = $global:fback
    $global:_FNC[$xfiles] = "MENU_VER"

    _OP_
}

function RUN_SCRIPT {
    Clear-Host
    Write-Host -ForegroundColor Green "Script selected $($global:_OP[[int]$op])"

    Write-Host ""
    Write-Host "Please set the `"godot`" directory"
    Write-Host "(Example: `"C:/my_folder/godot`")"
    Write-Host ""
    $gd = Read-Host "Godot directory"
    Write-Host "Trying use the godot directory: $gd"
    Write-Host "Starting run Godot Secure Script..."
    Write-Host ""
    & $__PY__ "$__DIR__\$fscript\$($_OP[[int]$op])" $gd
    Write-Host ""
    Write-Host "Operation ended, back to main menu."
    Pause
    INIT
}

function MENU_RESTORE {
    Clear-Host
    Write-Host -ForegroundColor Cyan "===================================="
    Write-Host -ForegroundColor Cyan "        RESTORE BACKUP"
    Write-Host -ForegroundColor Cyan "===================================="
    Write-Host "Are you sure restore backup?"
    Write-Host ""
    
    $global:_OP = @{}
    $global:_OP[0] = 2
    $global:_OP[1] = "Yes"
    $global:_OP[2] = "No"

    $global:_FNC = @{}
    $global:_FNC[0] = "MENU_RESTORE"
    $global:_FNC[1] = "RESTORE_BACKUP"
    $global:_FNC[2] = "INIT"

    _OP_
}

function RESTORE_BACKUP {
    Clear-Host
    Write-Host -ForegroundColor Green "Starting Restore Backup..."
    Write-Host ""
    Write-Host "Please set the `"godot`" directory"
    Write-Host "(Example: `"C:/my_folder/godot`")"
    Write-Host ""

    $gd = Read-Host "Godot directory"
    Write-Host "Trying use the godot directory: $gd"
    & $__PY__ "$__DIR__\utils\restore_backup.py" $gd
    Write-Host ""
    Write-Host "Operation ended, back to main menu."
    Pause

    INIT
}

# :: X0 SIGTERM
# :: ========================================================
function EXIT_FUNC {
    Write-Host "Exiting..."
    Start-Sleep -Seconds 2
    exit
}

INIT