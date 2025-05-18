import sys
import os

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and PyInstaller.
    The relative_path should be relative to your project root or resource folder.
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.normpath(os.path.join(base_path, relative_path))

def get_base_dir():
    """
    Returns the base directory path depending on frozen state.
    """
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
