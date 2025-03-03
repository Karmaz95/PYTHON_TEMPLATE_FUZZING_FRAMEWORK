"""
Payload History Cleaner
----------------------

Clean the payload history directory using PATH_PAYLOAD_HISTORY_LOG from config.py

Usage:
    python cleaner.py

WARNING:
    DO NOT RUN THIS SCRIPT IF YOU RECENTLY DISCOVERED A CRASH!
    It will permanently delete all payload history, including potential POC files.
"""

import shutil
from pathlib import Path
from config import PATH_PAYLOAD_HISTORY_LOG

def clean():
    """
    Cleans the payload history directory.

    This function removes all files and subdirectories in the payload history
    directory specified by PATH_PAYLOAD_HISTORY_LOG and recreates an empty directory.

    Raises:
        Exception: If there is an error during the cleaning process.
    """
    try:
        path = Path(PATH_PAYLOAD_HISTORY_LOG)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
        path.mkdir(exist_ok=True)
        print(f"Cleaned {path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clean()
