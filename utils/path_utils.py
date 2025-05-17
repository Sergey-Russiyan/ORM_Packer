# utils/path_utils.py
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_base_dir():
    """
    Returns the base directory path depending on whether the app is
    frozen (PyInstaller) or running as source code.
    """
    if getattr(sys, 'frozen', False):
        # When frozen by PyInstaller, _MEIPASS is the temporary folder
        return getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    else:
        # Running from source
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
