import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import backup

# ================================================================================
# restore_backup.py
#
# DESCRIPTION:      Script for restore backup files created for Godot-Secure.
# AUTOR:            Twister
# YEAR:             2026
# VERSION:          1.0.0
# ================================================================================

# NOTE:
# restore_backup.py in v4.x.x - v4.5.x: duplicated file by backup_dat.json root dir ver. generation.


for path in backup.deserialize():
    backup.restore(path)