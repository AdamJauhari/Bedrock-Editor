import sys
import subprocess

def ensure_package(pkg):
    """Ensure a package is installed, install it if not available"""
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# Install required packages
for pkg in ["PyQt5", "nbtlib"]:
    ensure_package(pkg)

# Try to import amulet-nbt, but make it optional
try:
    from amulet_nbt import load as amulet_load
    AMULET_AVAILABLE = True
except ImportError:
    print("Warning: amulet-nbt not available, using nbtlib only")
    AMULET_AVAILABLE = False

# Import required modules
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTreeWidget, QTreeWidgetItem, 
    QAction, QMessageBox, QWidget, QVBoxLayout, QPushButton, QListWidget, 
    QLabel, QHBoxLayout, QSizePolicy, QLineEdit
)
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer
import nbtlib
import struct
