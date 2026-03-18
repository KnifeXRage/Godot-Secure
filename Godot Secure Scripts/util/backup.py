import shutil
import json
import os
import sys
import atexit

# ================================================================================
# backup.py
#
# DESCRIPTION:      Script backup files created for Godot-Secure.
# AUTOR:            Twister
# YEAR:             2026
# VERSION:          1.0.0
# ================================================================================


_suffix = ".back"
_file_backup = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "backup_dat.json")
_first = True
_override = False
_quiet = False
_files = []


def backup(origin_path):
    """
    Start Backup File/s

    :param origin_path (String)
    """

    global _suffix, _first, _override, _quiet, _files
    
    target = origin_path + _suffix
    is_backup = os.path.exists(target)
    
    if is_backup and _first:
        _first = False
        _override = _quiz()

    if (_override or not is_backup) and os.path.exists(origin_path):
        shutil.copy2(origin_path, target)

        if not _quiet:
            print(f"Backup origin file in: {target}")

        _files.append(origin_path)


def restore(path):
    """
    Restore a Pre-Backup File

    :param path (String)
    """

    global _quiet

    backup_target = path + _suffix

    if os.path.exists(backup_target):
        os.replace(backup_target, path)

        if not _quiet:
            print(f"Restored file: {path}")
            
            
    elif not _quiet:
        print(f"Error!, can`t restore file: {path}")

        
        
def get_suffix():
    return _suffix


def serialize():
    global _files
    
    files = deserialize(False)

    _set = set(_files)

    for path in files:
        _set.add(path)

    _files = list(_set)

    if len(_files) > 0:
        
        try:
            with open(_file_backup, "w") as file:
                json.dump(_files, file)
                print(f"Backup files track created in:\n{_file_backup}")

        except:
            print(f"Error, can`t create {_file_backup}")


def deserialize(show_exist_error = True):
    files = []
    
    if os.path.exists(_file_backup):
        try:
            with open(_file_backup, "r") as file:
                files = json.load(file)

            if len(files) < 1:
                print("Not aviable files backup!")

        except:
            # F for respect, it's time to pray for all the brave bits lost in action.
            print(f"Can not open {_file_backup}, corrupted data?")

            x = 0
            while os.path.exists(_file_backup + f".corrupt{x}"):
                x += 1

            os.rename(_file_backup, _file_backup + f".corrupt{x}")

    elif show_exist_error:
        print(f"Backup Error, Not {_file_backup} found!")

    return files


def _init():
    global _quiet

    args = sys.argv[1:]
    _quiet = "-q" in args or "--quiet" in args

    atexit.register(serialize)

    if __name__ == "__main__":
        files = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

        if len(files) == 0:
            print("Not valid path files for backup!")
            return

        for file in files:
            if os.path.exists(file):
                backup(file)
            else:
                print(f"Not is valid or not exist file: {file}")


def _quiz(message="\nCAUTION: Backup already exist!\nYou want ovewrite it? (Not Recommended if you didn't update godot core vanilla: use 'n' for not overwrite)\nOverwrite Backup?"):
    while True:
        out = input(f"{message} (y/n): ").lower().strip()

        if out in ['y', 'yes']:
            return True
        if out in ['n', 'no', 'not']:
            return False
        
        print("Please confirm with 'y' for yes or 'n' for not.")


_init()