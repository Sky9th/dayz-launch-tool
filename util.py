import os
import sys
from PySide6.QtCore import QMetaObject, Qt


def get_resource_path(relative_path):
    """Get the absolute path to a resource."""
    if getattr(sys, 'frozen', False):
        # If running as a bundled executable
        base_path = sys._MEIPASS
    else:
        # If running as a script
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)