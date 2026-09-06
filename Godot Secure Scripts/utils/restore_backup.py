import os
import sys


## File Paths identical to those of the Godot-Secure scripts.
## It is assumed that it may vary at some point in the version of Godot-Secure.

MODIFICATIONS = [
    "version.py"
    ,"editor/export/project_export.cpp"
    ,"core/io/file_access_pack.h"
    ,"core/io/file_access_encrypted.h"
    ,"core/io/file_access_encrypted.cpp"
    ,"modules/gdscript/gdscript_tokenizer.h"

    #Camellia Modifications Files
    ,"core/crypto/crypto_core.h"
    ,"core/crypto/crypto_core.cpp"
]

CAMELLIA = [
    # Use for suprime warn if used AES
    "core/crypto/crypto_core.h"
    ,"core/crypto/crypto_core.cpp"
]

SECURITY_TOKEN_PATH = "core/crypto/security_token.h"

## Default Godot-Secure Log Colors
class LogColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    ## Default Godot-Secure Validations
    godot_root = ""

    if len(sys.argv) == 1:
        # No argument provided, use current directory
        godot_root = os.getcwd()
        print("\nNo directory specified. Using current directory as Godot Source Root.")
    elif len(sys.argv) == 2:
        # One argument provided, use it as Godot root
        godot_root = sys.argv[1]
    else:
        # Too many arguments provided
        print("\nUsage: python restore_backup.py <godot_source_root>")
        try:
            exit = input("\nPress Enter key to exit...")
        except EOFError:
            pass
        sys.exit(1)

    # Check for required Godot source fpr restore components
    core_dir = os.path.join(godot_root, "core")
    sconstruct_file = os.path.join(godot_root, "SConstruct")

    if not (os.path.isdir(core_dir) and os.path.isfile(sconstruct_file)):
        print(f"{LogColors.FAIL}Error: No valid Godot Source Detected in the Specified Directory.{LogColors.ENDC}")
        try:
            exit = input("\nPress Enter key to exit...")
        except EOFError:
            pass
        sys.exit(1)

    print(f"\nUsing Godot Source Root: {godot_root}")
    print(f"{LogColors.WARNING} Make Sure To Backup Your Previous Generated Credentials (i.e. Tokens, Algorithms, etc) {LogColors.ENDC}")
    confirm = input(f"\n\n ⚠   {LogColors.WARNING}Start Godot Source Restore Operations {LogColors.ENDC}{LogColors.FAIL}(y/n)?{LogColors.ENDC}: ").strip().lower()
    if not (confirm == 'y' or confirm == 'yes'):
        print("Closing Restore Script...")
        try:
            exit = input("\nPress Enter key to exit...")
        except EOFError:
            pass
        sys.exit(1)

    for file in MODIFICATIONS:
        file_path = os.path.join(godot_root, file)
        file_path_backup = file_path + ".backup"

        if not os.path.exists(file_path_backup):
            if not(file in CAMELLIA):
              print(f"{LogColors.WARNING} Can`t found backup file for {LogColors.FAIL}{file_path}{LogColors.ENDC}")
            continue

        if os.path.exists(file_path):
            os.replace(file_path_backup, file_path)
            print(f"{LogColors.OKGREEN} Restore backup file {LogColors.BOLD}{file_path}{LogColors.ENDC}")
        else:
            # User manual remove file
            os.rename(file_path_backup, file_path)
            print(f"{LogColors.WARNING}Created file using backup {LogColors.BOLD}{file_path}{LogColors.ENDC}")

    # Manually Remove Security Token File
    if not os.path.exists(SECURITY_TOKEN_PATH):
        os.remove(os.path.join(godot_root, SECURITY_TOKEN_PATH))
        print(f"{LogColors.OKGREEN} Removed file {LogColors.BOLD}{SECURITY_TOKEN_PATH}{LogColors.ENDC}")