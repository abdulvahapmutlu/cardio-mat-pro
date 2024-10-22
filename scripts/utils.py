# scripts/utils.py

import os

def find_record_path(records_path, record_name):
    """
    Search the subdirectories in records_path to find the correct file.

    Parameters:
    - records_path (str): Path to the records directory.
    - record_name (str): Name of the record to find.

    Returns:
    - str or None: Full path to the record without extension if found, else None.
    """
    for subdir, _, files in os.walk(records_path):
        for file in files:
            if file.startswith(record_name):
                return os.path.join(subdir, file.rsplit('.', 1)[0])
    return None
